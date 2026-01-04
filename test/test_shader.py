import ctypes
import sys
from contextlib import ExitStack

import emath
import pytest
from emath import DArray
from emath import FArray
from emath import I32Array
from emath import U32Array
from emath import UVector2
from OpenGL.GL import GL_SHADER_STORAGE_BUFFER_BINDING
from OpenGL.GL import glGetIntegeri_v
from OpenGL.GL import glGetUniformfv
from OpenGL.GL import glGetUniformiv
from OpenGL.GL import glGetUniformLocation
from OpenGL.GL import glIsProgram

from egraphics import ComputeShader
from egraphics import GBuffer
from egraphics import Shader
from egraphics import ShaderAttribute
from egraphics import ShaderStorageBlock
from egraphics import ShaderUniform
from egraphics import Texture
from egraphics import Texture2d
from egraphics import TextureComponents


def test_empty_shader(platform):
    with pytest.raises(TypeError) as excinfo:
        Shader()
    assert str(excinfo.value) == ("vertex, geometry or fragment must be provided")


@pytest.mark.parametrize("stage", ["vertex", "fragment"])
def test_compile_error(platform, stage):
    with pytest.raises(RuntimeError) as excinfo:
        Shader(
            **{
                stage: b"""#version 140
            void main()
            {
                what--what
            }
            """
            }
        )
    assert str(excinfo.value).startswith(f"{stage} stage failed to compile:\n")


def test_link_error(platform):
    with pytest.raises(RuntimeError) as excinfo:
        Shader(
            vertex=f"""
            #version 140
            vec4 some_function_that_doesnt_exist();
            void main()
            {{
                gl_Position = some_function_that_doesnt_exist();
            }}
            """.encode("utf-8")
        )
    assert str(excinfo.value).startswith(f"failed to link:\n")


def test_vertex_only(platform):
    shader = Shader(
        vertex=b"""#version 140
    void main()
    {
        gl_Position = vec4(0, 0, 0, 1);
    }
    """
    )


def test_geometry_only(platform):
    with pytest.raises(TypeError) as excinfo:
        shader = Shader(
            geometry=b"""#version 150
        layout(triangles) in;
        layout(triangle_strip) out;

        void main()
        {
            gl_Position = vec4(0, 0, 0, 1);
        }
        """
        )
    assert str(excinfo.value) == "geometry shader requires vertex shader"


def test_fragment_only(platform):
    shader = Shader(
        fragment=b"""#version 140
    out vec4 FragColor;
    void main()
    {
        FragColor = vec4(0, 0, 0, 1);
    }
    """
    )


def test_vertex_and_fragment(platform):
    shader = Shader(
        vertex=b"""#version 140
    void main()
    {
        gl_Position = vec4(0, 0, 0, 1);
    }
    """,
        fragment=b"""#version 330
    out vec4 FragColor;
    void main()
    {
        FragColor = vec4(0, 0, 0, 1);
    }
    """,
    )


def test_delete(platform):
    shader = Shader(
        vertex=b"""#version 140
    void main()
    {
        gl_Position = vec4(0, 0, 0, 1);
    }
    """
    )
    shader._activate()

    gl_program = shader._gl_program

    assert glIsProgram(gl_program)
    del shader
    assert not glIsProgram(gl_program)


def test_gl_attributes_and_uniforms(platform):
    shader = Shader(
        vertex=f"""#version 140

    void main()
    {{
        gl_Position = vec4(gl_VertexID, 0, gl_DepthRange.near, 1);
    }}
    """.encode("utf-8")
    )
    assert len(shader.attributes) == 0
    assert len(shader.uniforms) == 0


@pytest.mark.parametrize("location", [None, 1])
@pytest.mark.parametrize(
    "glsl_type, python_type",
    [
        ("float", ctypes.c_float),
        ("double", ctypes.c_double),
        ("int", ctypes.c_int32),
        ("uint", ctypes.c_uint32),
    ],
)
@pytest.mark.parametrize("array", [False, True])
def test_pod_attributes(platform, gl_version, location, glsl_type, python_type, array):
    glsl_version = "140"
    if location is not None or array:
        glsl_version = "330 core"
        if gl_version < (3, 3):
            pytest.xfail()

    if glsl_type == "double":
        glsl_version = "410 core"
        if gl_version < (4, 1):
            pytest.xfail()

    if location is None:
        layout = ""
    else:
        layout = f"layout(location={location})"
    if array:
        array_def = "[2]"
        x_value = "attr_name[0]"
        y_value = "attr_name[1]"
    else:
        array_def = ""
        x_value = "attr_name"
        y_value = "0"
    shader = Shader(
        vertex=f"""#version {glsl_version}
    {layout} in {glsl_type} attr_name{array_def};
    void main()
    {{
        gl_Position = vec4({x_value}, {y_value}, 0, 1);
    }}
    """.encode("utf-8")
    )
    attr = shader["attr_name"]
    assert len(shader.attributes) == 1
    assert shader.attributes[0] is attr
    assert isinstance(attr, ShaderAttribute)
    assert attr.name == "attr_name"
    assert attr.data_type is python_type
    assert attr.size == (2 if array else 1)
    assert attr.location == (0 if location is None else location)


@pytest.mark.parametrize("location", [None, 1])
@pytest.mark.parametrize(
    "glsl_type, python_type, array_type",
    [
        ("float", ctypes.c_float, FArray),
        ("double", ctypes.c_double, DArray),
        ("int", ctypes.c_int32, I32Array),
        ("uint", ctypes.c_uint32, U32Array),
        ("bool", ctypes.c_bool, I32Array),
    ],
)
@pytest.mark.parametrize("array", [False, True])
@pytest.mark.parametrize(
    "shader_cls, shader_kwargs, expected_uniform_count",
    [
        (
            Shader,
            {
                "vertex": """#version {glsl_version}
{layout} uniform {glsl_type} uni_name{array_def};
void main()
{{
    gl_Position = vec4({x_value}, {y_value}, 0, 1);
}}
    """
            },
            1,
        ),
        (
            ComputeShader,
            {
                "compute": """#version {glsl_version}
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
{layout} uniform {glsl_type} uni_name{array_def};
layout(rgba32f, binding=0, location=10) uniform image2D result;
void main()
{{
    imageStore(result, ivec2(0, 0), vec4({x_value}, {y_value}, 0, 1));
}}
    """
            },
            2,
        ),
    ],
)
def test_pod_uniforms(
    platform,
    gl_version,
    location,
    glsl_type,
    python_type,
    array_type,
    array,
    shader_cls,
    shader_kwargs,
    expected_uniform_count,
):
    glsl_version = "140"

    if glsl_type == "double":
        glsl_version = "400 core"
        if gl_version < (4, 0):
            pytest.xfail()

    if location is not None or shader_cls is ComputeShader:
        glsl_version = "430 core"
        if gl_version < (4, 3):
            pytest.xfail()

    if location is None:
        layout = ""
    else:
        layout = f"layout(location={location})"
    if array:
        array_def = "[2]"
        x_value = "uni_name[0]"
        y_value = "uni_name[1]"
    else:
        array_def = ""
        x_value = "uni_name"
        y_value = "0"
    try:
        print(
            {
                k: v.format(
                    glsl_version=glsl_version,
                    glsl_type=glsl_type,
                    array_def=array_def,
                    x_value=x_value,
                    y_value=y_value,
                    layout=layout,
                )
                for k, v in shader_kwargs.items()
            }["compute"]
        )
    except KeyError:
        pass
    shader = shader_cls(
        **{
            k: v.format(
                glsl_version=glsl_version,
                glsl_type=glsl_type,
                array_def=array_def,
                x_value=x_value,
                y_value=y_value,
                layout=layout,
            ).encode("utf-8")
            for k, v in shader_kwargs.items()
        }
    )
    uni = shader["uni_name"]
    assert len(shader.uniforms) == expected_uniform_count
    assert uni in shader.uniforms
    assert isinstance(uni, ShaderUniform)
    assert uni.name == "uni_name"
    assert uni.data_type is python_type
    assert uni.size == (2 if array else 1)
    assert uni.location == (0 if location is None else location)

    shader._activate()
    with ExitStack() as exit_stack:
        with pytest.raises(ValueError) as excinfo:
            shader._set_uniform(uni, None, exit_stack)
        assert (
            str(excinfo.value)
            == f"expected {python_type} or {array_type} for uni_name (got {type(None)})"
        )

        if array:
            shader._set_uniform(uni, array_type(0, 1), exit_stack)
            get_value_0 = ctypes.c_float()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_float()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == 0
            assert get_value_1.value == 1

            shader._set_uniform(uni, array_type(1), exit_stack)
            get_value_0 = ctypes.c_float()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_float()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == 1
            assert get_value_1.value == 1

            shader._set_uniform(uni, array_type(), exit_stack)
            get_value_0 = ctypes.c_float()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_float()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == 1
            assert get_value_1.value == 1

            shader._set_uniform(uni, python_type(0), exit_stack)
            get_value_0 = ctypes.c_float()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_float()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == 0
            assert get_value_1.value == 1

            shader._set_uniform(uni, array_type(1, 0, 0), exit_stack)
            get_value_0 = ctypes.c_float()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_float()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == 1
            assert get_value_1.value == 0
        else:
            shader._set_uniform(uni, python_type(1), exit_stack)
            get_value = ctypes.c_float()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            assert get_value.value == 1

            shader._set_uniform(uni, array_type(), exit_stack)
            get_value = ctypes.c_float()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            assert get_value.value == 1

            shader._set_uniform(uni, array_type(0), exit_stack)
            get_value = ctypes.c_float()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            assert get_value.value == 0

            shader._set_uniform(uni, array_type(1, 0), exit_stack)
            get_value = ctypes.c_float()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            assert get_value.value == 1


@pytest.mark.parametrize("location", [None, 1])
@pytest.mark.parametrize("prefix", ["", "i", "u"])
@pytest.mark.parametrize(
    "postfix, components",
    [
        ("1D", 1),
        ("2D", 2),
        ("3D", 3),
        ("Cube", 3),
        ("2DRect", 2),
        ("1DArray", 2),
        ("2DArray", 3),
        ("CubeArray", 4),
        ("Buffer", 1),
        ("2DMS", 2),
        ("2DMSArray", 3),
    ],
)
@pytest.mark.parametrize("array", [False, True])
@pytest.mark.parametrize(
    "shader_cls, shader_kwargs, expected_uniform_count",
    [
        (
            Shader,
            {
                "vertex": """#version {glsl_version}
{layout} uniform {prefix}sampler{postfix} uni_name{array_def};
void main()
{{
    gl_Position = vec4({x_value}, {y_value}, 0, 1);
}}
    """
            },
            1,
        ),
        (
            ComputeShader,
            {
                "compute": """#version {glsl_version}
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
{layout} uniform {prefix}sampler{postfix} uni_name{array_def};
layout(rgba32f, binding=0, location=10) uniform image2D result;
void main()
{{
    imageStore(result, ivec2(0, 0), vec4({x_value}, {y_value}, 0, 1));
}}
    """
            },
            2,
        ),
    ],
)
def test_sampler_uniforms(
    platform,
    gl_version,
    location,
    prefix,
    postfix,
    components,
    array,
    shader_cls,
    shader_kwargs,
    expected_uniform_count,
):
    glsl_version = "140"

    if postfix in ["2DMS", "2DMSArray"]:
        glsl_version = "150"
        if gl_version < (3, 2):
            pytest.xfail()

    if postfix == "CubeArray":
        glsl_version = "400 core"
        if gl_version < (4, 0):
            pytest.xfail()

    if location is not None or shader_cls is ComputeShader:
        glsl_version = "430 core"
        if gl_version < (4, 3):
            pytest.xfail()

    if location is None:
        layout = ""
    else:
        layout = f"layout(location={location})"
    texture_function = "texture"
    if postfix in ["Buffer", "2DMS", "2DMSArray"]:
        texture_function = "texelFetch"
    texture_lookup = ", ".join("0" * components)
    if components > 1:
        texture_lookup = f"vec{components}({texture_lookup})"
    if postfix in ["2DMS", "2DMSArray"]:
        texture_lookup = f"i{texture_lookup}, 0"
    if array:
        array_def = "[2]"
        x_value = f"{texture_function}(uni_name[0], {texture_lookup}).r"
        y_value = f"{texture_function}(uni_name[1], {texture_lookup}).r"
    else:
        array_def = ""
        x_value = f"{texture_function}(uni_name, {texture_lookup}).r"
        y_value = "0"
    shader = shader_cls(
        **{
            k: v.format(
                glsl_version=glsl_version,
                layout=layout,
                prefix=prefix,
                postfix=postfix,
                array_def=array_def,
                x_value=x_value,
                y_value=y_value,
            ).encode("utf-8")
            for k, v in shader_kwargs.items()
        }
    )
    uni = shader["uni_name"]
    assert len(shader.uniforms) == expected_uniform_count
    assert uni in shader.uniforms
    assert isinstance(uni, ShaderUniform)
    assert uni.name == "uni_name"
    assert uni.data_type is Texture
    assert uni.size == (2 if array else 1)
    assert uni.location == (0 if location is None else location)

    shader._activate()
    with ExitStack() as exit_stack:
        with pytest.raises(ValueError) as excinfo:
            shader._set_uniform(uni, None, exit_stack)
        assert str(excinfo.value) == (
            f"expected {Texture} or sequence of {Texture} for uni_name (got {type(None)})"
        )

        bad_value = ["1", "2"]
        with pytest.raises(ValueError) as excinfo:
            shader._set_uniform(uni, bad_value, exit_stack)
        assert str(excinfo.value) == (
            f"expected {Texture} or sequence of {Texture} for uni_name (got {bad_value!r})"
        )

        tex1 = Texture2d(UVector2(1, 1), TextureComponents.R, ctypes.c_uint8, b"\x00")
        tex2 = Texture2d(UVector2(1, 1), TextureComponents.R, ctypes.c_uint8, b"\x00")
        tex3 = Texture2d(UVector2(1, 1), TextureComponents.R, ctypes.c_uint8, b"\x00")

        if array:
            shader._set_uniform(uni, [tex1, tex2], exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex1._texture_unit
            assert get_value_1.value == tex2._texture_unit

            shader._set_uniform(uni, [tex3], exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex3._texture_unit
            assert get_value_1.value == tex2._texture_unit

            shader._set_uniform(uni, tex1, exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex1._texture_unit
            assert get_value_1.value == tex2._texture_unit

            shader._set_uniform(uni, [], exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex1._texture_unit
            assert get_value_1.value == tex2._texture_unit

            shader._set_uniform(uni, [tex3, tex1, tex2], exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex3._texture_unit
            assert get_value_1.value == tex1._texture_unit
        else:
            shader._set_uniform(uni, tex1, exit_stack)
            get_value = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value)
            assert get_value.value == tex1._texture_unit

            shader._set_uniform(uni, [tex2], exit_stack)
            get_value = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value)
            assert get_value.value == tex2._texture_unit

            shader._set_uniform(uni, [tex1, tex3], exit_stack)
            get_value = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value)
            assert get_value.value == tex1._texture_unit

            shader._set_uniform(uni, [], exit_stack)
            get_value = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value)
            assert get_value.value == tex1._texture_unit


@pytest.mark.parametrize("location", [None, 1])
@pytest.mark.parametrize(
    "postfix, components",
    [
        ("1DShadow", 3),
        ("2DShadow", 3),
        ("CubeShadow", 4),
        ("2DRectShadow", 3),
        ("1DArrayShadow", 3),
        ("2DArrayShadow", 4),
    ],
)
@pytest.mark.parametrize("array", [False, True])
@pytest.mark.parametrize(
    "shader_cls, shader_kwargs, expected_uniform_count",
    [
        (
            Shader,
            {
                "vertex": """#version {glsl_version}
{layout} uniform sampler{postfix} uni_name{array_def};
void main()
{{
    gl_Position = vec4({x_value}, {y_value}, 0, 1);
}}
    """
            },
            1,
        ),
        (
            ComputeShader,
            {
                "compute": """#version {glsl_version}
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
{layout} uniform sampler{postfix} uni_name{array_def};
layout(rgba32f, binding=0, location=10) uniform image2D result;
void main()
{{
    imageStore(result, ivec2(0, 0), vec4({x_value}, {y_value}, 0, 1));
}}
    """
            },
            2,
        ),
    ],
)
def test_shadow_sampler_uniforms(
    platform,
    gl_version,
    location,
    postfix,
    components,
    array,
    shader_cls,
    shader_kwargs,
    expected_uniform_count,
):
    glsl_version = "140"

    if location is not None or shader_cls is ComputeShader:
        glsl_version = "430 core"
        if gl_version < (4, 3):
            pytest.xfail()

    if location is None:
        layout = ""
    else:
        layout = f"layout(location={location})"
    texture_lookup = ", ".join("0" * components)
    if components > 1:
        texture_lookup = f"vec{components}({texture_lookup})"
    if array:
        array_def = "[2]"
        x_value = f"texture(uni_name[0], {texture_lookup})"
        y_value = f"texture(uni_name[1], {texture_lookup})"
    else:
        array_def = ""
        x_value = f"texture(uni_name, {texture_lookup})"
        y_value = "0"
    shader = shader_cls(
        **{
            k: v.format(
                glsl_version=glsl_version,
                layout=layout,
                postfix=postfix,
                array_def=array_def,
                x_value=x_value,
                y_value=y_value,
            ).encode("utf-8")
            for k, v in shader_kwargs.items()
        }
    )
    uni = shader["uni_name"]
    assert len(shader.uniforms) == expected_uniform_count
    assert uni in shader.uniforms
    assert isinstance(uni, ShaderUniform)
    assert uni.name == "uni_name"
    assert uni.data_type is Texture
    assert uni.size == (2 if array else 1)
    assert uni.location == (0 if location is None else location)

    shader._activate()
    with ExitStack() as exit_stack:
        with pytest.raises(ValueError) as excinfo:
            shader._set_uniform(uni, None, exit_stack)
        assert str(excinfo.value) == (
            f"expected {Texture} or sequence of {Texture} for uni_name (got {type(None)})"
        )

        bad_value = ["1", "2"]
        with pytest.raises(ValueError) as excinfo:
            shader._set_uniform(uni, bad_value, exit_stack)
        assert str(excinfo.value) == (
            f"expected {Texture} or sequence of {Texture} for uni_name (got {bad_value!r})"
        )

        tex1 = Texture2d(UVector2(1, 1), TextureComponents.R, ctypes.c_uint8, b"\x00")
        tex2 = Texture2d(UVector2(1, 1), TextureComponents.R, ctypes.c_uint8, b"\x00")
        tex3 = Texture2d(UVector2(1, 1), TextureComponents.R, ctypes.c_uint8, b"\x00")

        if array:
            shader._set_uniform(uni, [tex1, tex2], exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex1._texture_unit
            assert get_value_1.value == tex2._texture_unit

            shader._set_uniform(uni, [tex3], exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex3._texture_unit
            assert get_value_1.value == tex2._texture_unit

            shader._set_uniform(uni, tex1, exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex1._texture_unit
            assert get_value_1.value == tex2._texture_unit

            shader._set_uniform(uni, [], exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex1._texture_unit
            assert get_value_1.value == tex2._texture_unit

            shader._set_uniform(uni, [tex3, tex1, tex2], exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex3._texture_unit
            assert get_value_1.value == tex1._texture_unit
        else:
            shader._set_uniform(uni, tex1, exit_stack)
            get_value = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value)
            assert get_value.value == tex1._texture_unit

            shader._set_uniform(uni, [tex2], exit_stack)
            get_value = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value)
            assert get_value.value == tex2._texture_unit

            shader._set_uniform(uni, [tex1, tex3], exit_stack)
            get_value = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value)
            assert get_value.value == tex1._texture_unit

            shader._set_uniform(uni, [], exit_stack)
            get_value = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value)
            assert get_value.value == tex1._texture_unit


@pytest.mark.parametrize("location", [None, 1])
@pytest.mark.parametrize(
    "postfix, components",
    [("2D", 2), ("3D", 3), ("Cube", 3), ("2DArray", 3), ("Buffer", 1), ("CubeArray", 3)],
)
@pytest.mark.parametrize("array", [False, True])
@pytest.mark.parametrize(
    "shader_cls, shader_kwargs, expected_uniform_count",
    [
        (
            Shader,
            {
                "vertex": """#version 430 core
in vec2 xy;
void main()
{{
    gl_Position = vec4(xy, 0, 1);
}}
""",
                "fragment": """#version 430 core
{layout} uniform image{postfix} uni_name{array_def};
out vec4 FragColor;
void main()
{{
    vec4 val = imageLoad(uni_name{texture_access}, {coord_expr});
    FragColor = vec4({x_value}, {y_value}, 0, 1);
}}
    """,
            },
            1,
        ),
        (
            ComputeShader,
            {
                "compute": """#version 430 core
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
{layout} uniform image{postfix} uni_name{array_def};
layout(rgba32f, location=10, binding=0) uniform image2D result;
void main()
{{
    vec4 val = imageLoad(uni_name{texture_access}, {coord_expr});
    imageStore(result, ivec2(0, 0), vec4({x_value}, {y_value}, val.r, 1));
}}
    """
            },
            2,
        ),
    ],
)
def test_image_uniforms(
    platform,
    gl_version,
    location,
    postfix,
    components,
    array,
    shader_cls,
    shader_kwargs,
    expected_uniform_count,
):
    glsl_version = "430 core"
    if gl_version < (4, 3):
        pytest.xfail()

    if location is None:
        layout = "layout(rgba32f)"
    else:
        layout = f"layout(rgba32f, location={location})"

    if postfix == "Buffer":
        coord = "0"
        coord_expr = "0"
    else:
        coord = f"ivec{components}({', '.join('0' * components)})"
        coord_expr = coord

    if array:
        array_def = "[2]"
        texture_access = "[0]"
        x_value = f"imageLoad(uni_name[0], {coord}).r"
        y_value = f"imageLoad(uni_name[1], {coord}).r"
    else:
        array_def = ""
        texture_access = ""
        x_value = f"imageLoad(uni_name, {coord}).r"
        y_value = "0"

    shader = shader_cls(
        **{
            k: v.format(
                glsl_version=glsl_version,
                layout=layout,
                postfix=postfix,
                array_def=array_def,
                coord_expr=coord_expr,
                texture_access=texture_access,
                x_value=x_value,
                y_value=y_value,
            ).encode("utf-8")
            for k, v in shader_kwargs.items()
        }
    )
    uni = shader["uni_name"]
    assert len(shader.uniforms) == expected_uniform_count
    assert uni in shader.uniforms
    assert isinstance(uni, ShaderUniform)
    assert uni.name == "uni_name"
    assert uni.data_type is Texture
    assert uni.size == (2 if array else 1)
    assert uni.location == (0 if location is None else location)
    assert uni._is_image

    shader._activate()
    with ExitStack() as exit_stack:
        with pytest.raises(ValueError) as excinfo:
            shader._set_uniform(uni, None, exit_stack)
        assert str(excinfo.value) == (
            f"expected {Texture} or sequence of {Texture} for uni_name (got {type(None)})"
        )

        bad_value = ["1", "2"]
        with pytest.raises(ValueError) as excinfo:
            shader._set_uniform(uni, bad_value, exit_stack)
        assert str(excinfo.value) == (
            f"expected {Texture} or sequence of {Texture} for uni_name (got {bad_value!r})"
        )

        tex1 = Texture2d(UVector2(1, 1), TextureComponents.XYZW, ctypes.c_float, b"\x00" * 16)
        tex2 = Texture2d(UVector2(1, 1), TextureComponents.XYZW, ctypes.c_float, b"\x00" * 16)
        tex3 = Texture2d(UVector2(1, 1), TextureComponents.XYZW, ctypes.c_float, b"\x00" * 16)

        if array:
            shader._set_uniform(uni, [tex1, tex2], exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex1._image_unit
            assert get_value_1.value == tex2._image_unit

            shader._set_uniform(uni, [tex3], exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex3._image_unit
            assert get_value_1.value == tex2._image_unit

            shader._set_uniform(uni, tex1, exit_stack)
            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex1._image_unit
            assert get_value_1.value == tex2._image_unit
        else:
            shader._set_uniform(uni, tex1, exit_stack)
            get_value = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value)
            assert get_value.value == tex1._image_unit

            shader._set_uniform(uni, tex2, exit_stack)
            get_value = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value)
            assert get_value.value == tex2._image_unit


@pytest.mark.parametrize("location", [None, 1])
@pytest.mark.parametrize("components", [2, 3, 4])
@pytest.mark.parametrize(
    "glsl_prefix, emath_prefix", [("", "F"), ("d", "D"), ("i", "I32"), ("u", "U32")]
)
@pytest.mark.parametrize("array", [False, True])
def test_vector_attributes(
    platform, gl_version, location, components, glsl_prefix, emath_prefix, array
):
    glsl_version = "140"

    if location is not None:
        glsl_version = "330 core"
        if gl_version < (3, 3):
            pytest.xfail()

    if array:
        glsl_version = "400 core"
        if gl_version < (4, 0):
            pytest.xfail()

    if glsl_prefix == "d":
        glsl_version = "410 core"
        if gl_version < (4, 1):
            pytest.xfail()

    if location is None:
        layout = ""
    else:
        layout = f"layout(location={location})"
    if array:
        array_def = "[2]"
        x_value = "attr_name[0].x"
        y_value = "attr_name[1].x"
    else:
        array_def = ""
        x_value = "attr_name.x"
        y_value = "0"
    shader = Shader(
        vertex=f"""#version {glsl_version}
    {layout} in {glsl_prefix}vec{components} attr_name{array_def};
    void main()
    {{
        gl_Position = vec4({x_value}, {y_value}, 0, 1);
    }}
    """.encode("utf-8")
    )
    attr = shader["attr_name"]
    assert len(shader.attributes) == 1
    assert shader.attributes[0] is attr
    assert isinstance(attr, ShaderAttribute)
    assert attr.name == "attr_name"
    assert attr.data_type is getattr(emath, f"{emath_prefix}Vector{components}")
    assert attr.size == (2 if array else 1)
    assert attr.location == (0 if location is None else location)


@pytest.mark.parametrize("location", [None, 1])
@pytest.mark.parametrize("components", [2, 3, 4])
@pytest.mark.parametrize(
    "glsl_prefix, emath_prefix", [("", "F"), ("d", "D"), ("i", "I32"), ("u", "U32")]
)
@pytest.mark.parametrize("array", [False, True])
@pytest.mark.parametrize(
    "shader_cls, shader_kwargs, expected_uniform_count",
    [
        (
            Shader,
            {
                "vertex": """#version {glsl_version}
{layout} uniform {glsl_prefix}vec{components} uni_name{array_def};
void main()
{{
    gl_Position = vec4({x_value}, {y_value}, 0, 1);
}}
    """
            },
            1,
        ),
        (
            ComputeShader,
            {
                "compute": """#version {glsl_version}
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
{layout} uniform {glsl_prefix}vec{components} uni_name{array_def};
layout(rgba32f, binding=0, location=10) uniform image2D result;
void main()
{{
    imageStore(result, ivec2(0, 0), vec4({x_value}, {y_value}, 0, 1));
}}
    """
            },
            2,
        ),
    ],
)
def test_vector_uniforms(
    platform,
    gl_version,
    location,
    components,
    glsl_prefix,
    emath_prefix,
    array,
    shader_cls,
    shader_kwargs,
    expected_uniform_count,
):
    glsl_version = "140"

    if glsl_prefix == "d":
        glsl_version = "400 core"
        if gl_version < (4, 0):
            pytest.xfail()

    if location is not None or shader_cls is ComputeShader:
        glsl_version = "430 core"
        if gl_version < (4, 3):
            pytest.xfail()

    if location is None:
        layout = ""
    else:
        layout = f"layout(location={location})"
    if array:
        array_def = "[2]"
        x_value = "uni_name[0].x"
        y_value = "uni_name[1].x"
    else:
        array_def = ""
        x_value = "uni_name.x"
        y_value = "0"
    shader = shader_cls(
        **{
            k: v.format(
                glsl_version=glsl_version,
                layout=layout,
                glsl_prefix=glsl_prefix,
                components=components,
                array_def=array_def,
                x_value=x_value,
                y_value=y_value,
            ).encode("utf-8")
            for k, v in shader_kwargs.items()
        }
    )
    uni = shader["uni_name"]
    assert len(shader.uniforms) == expected_uniform_count
    assert uni in shader.uniforms
    assert isinstance(uni, ShaderUniform)
    assert uni.name == "uni_name"
    assert uni.data_type is getattr(emath, f"{emath_prefix}Vector{components}")
    assert uni.size == (2 if array else 1)
    assert uni.location == (0 if location is None else location)

    python_type = getattr(emath, f"{emath_prefix}Vector{components}")
    shader._activate()
    with ExitStack() as exit_stack:
        array_type = getattr(emath, python_type.__name__ + "Array")
        with pytest.raises(ValueError) as excinfo:
            shader._set_uniform(uni, None, exit_stack)
        assert (
            str(excinfo.value)
            == f"expected {python_type} or {array_type} for uni_name (got {type(None)})"
        )

        with pytest.raises(ValueError) as excinfo:
            shader._set_uniform(uni, ["1", "2"], exit_stack)
        assert (
            str(excinfo.value)
            == f"expected {python_type} or {array_type} for uni_name (got {list})"
        )

        if array:
            shader._set_uniform(uni, array_type(python_type(25), python_type(26)), exit_stack)
            get_value_0 = (ctypes.c_float * components)()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            for i in range(components):
                assert get_value_0[i] == 25
            get_value_1 = (ctypes.c_float * components)()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            for i in range(components):
                assert get_value_1[i] == 26

            shader._set_uniform(uni, array_type(python_type(27)), exit_stack)
            get_value_0 = (ctypes.c_float * components)()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            for i in range(components):
                assert get_value_0[i] == 27
            get_value_1 = (ctypes.c_float * components)()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            for i in range(components):
                assert get_value_1[i] == 26

            shader._set_uniform(uni, python_type(28), exit_stack)
            get_value_0 = (ctypes.c_float * components)()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            for i in range(components):
                assert get_value_0[i] == 28
            get_value_1 = (ctypes.c_float * components)()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            for i in range(components):
                assert get_value_1[i] == 26

            shader._set_uniform(uni, array_type(), exit_stack)
            get_value_0 = (ctypes.c_float * components)()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            for i in range(components):
                assert get_value_0[i] == 28
            get_value_1 = (ctypes.c_float * components)()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            for i in range(components):
                assert get_value_1[i] == 26

            shader._set_uniform(uni, array_type(python_type(29), python_type(30)), exit_stack)
            get_value_0 = (ctypes.c_float * components)()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            for i in range(components):
                assert get_value_0[i] == 29
            get_value_1 = (ctypes.c_float * components)()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            for i in range(components):
                assert get_value_1[i] == 30
        else:
            shader._set_uniform(uni, python_type(100), exit_stack)
            get_value = (ctypes.c_float * components)()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            for i in range(components):
                assert get_value[i] == 100

            shader._set_uniform(uni, array_type(python_type(101), python_type(102)), exit_stack)
            get_value = (ctypes.c_float * components)()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            for i in range(components):
                assert get_value[i] == 101

            shader._set_uniform(uni, array_type(), exit_stack)
            get_value = (ctypes.c_float * components)()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            for i in range(components):
                assert get_value[i] == 101

            shader._set_uniform(uni, array_type(python_type(102)), exit_stack)
            get_value = (ctypes.c_float * components)()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            for i in range(components):
                assert get_value[i] == 102


@pytest.mark.parametrize("location", [None, 1])
@pytest.mark.parametrize("rows", [2, 3, 4])
@pytest.mark.parametrize("columns", [2, 3, 4])
@pytest.mark.parametrize("glsl_prefix, emath_prefix", [("", "F"), ("d", "D")])
@pytest.mark.parametrize("array", [False, True])
def test_matrix_attributes(
    platform, gl_version, location, rows, columns, glsl_prefix, emath_prefix, array
):
    glsl_version = "140"

    if location is not None:
        glsl_version = "330 core"
        if gl_version < (3, 3):
            pytest.xfail()

    if array:
        glsl_version = "400 core"
        if gl_version < (4, 0):
            pytest.xfail()

    if glsl_prefix == "d":
        glsl_version = "410 core"
        if gl_version < (4, 1):
            pytest.xfail()

    # macos has problems with dmat3x3+ in arrays?
    if sys.platform == "darwin" and glsl_prefix == "d" and columns >= 3 and rows >= 3 and array:
        pytest.xfail()

    if location is None:
        layout = ""
    else:
        layout = f"layout(location={location})"
    if array:
        array_def = "[2]"
        x_value = "attr_name[0][0][0]"
        y_value = "attr_name[1][0][0]"
    else:
        array_def = ""
        x_value = "attr_name[0][0]"
        y_value = "0"
    shader = Shader(
        vertex=f"""#version {glsl_version}
    {layout} in {glsl_prefix}mat{rows}x{columns} attr_name{array_def};
    void main()
    {{
        gl_Position = vec4({x_value}, {y_value}, 0, 1);
    }}
    """.encode("utf-8")
    )
    attr = shader["attr_name"]
    assert len(shader.attributes) == 1
    assert shader.attributes[0] is attr
    assert isinstance(attr, ShaderAttribute)
    assert attr.name == "attr_name"
    assert attr.data_type is getattr(emath, f"{emath_prefix}Matrix{rows}x{columns}")
    assert attr.size == (2 if array else 1)
    assert attr.location == (0 if location is None else location)


@pytest.mark.parametrize("location", [None, 1])
@pytest.mark.parametrize("rows", [2, 3, 4])
@pytest.mark.parametrize("columns", [2, 3, 4])
@pytest.mark.parametrize("glsl_prefix, emath_prefix", [("", "F"), ("d", "D")])
@pytest.mark.parametrize("array", [False, True])
@pytest.mark.parametrize(
    "shader_cls, shader_kwargs, expected_uniform_count",
    [
        (
            Shader,
            {
                "vertex": """#version {glsl_version}
{layout} uniform {glsl_prefix}mat{rows}x{columns} uni_name{array_def};
void main()
{{
    gl_Position = vec4({x_value}, {y_value}, 0, 1);
}}
    """
            },
            1,
        ),
        (
            ComputeShader,
            {
                "compute": """#version {glsl_version}
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
{layout} uniform {glsl_prefix}mat{rows}x{columns} uni_name{array_def};
layout(rgba32f, binding=0, location=10) uniform image2D result;
void main()
{{
    imageStore(result, ivec2(0, 0), vec4({x_value}, {y_value}, 0, 1));
}}
    """
            },
            2,
        ),
    ],
)
def test_matrix_uniforms(
    platform,
    gl_version,
    location,
    rows,
    columns,
    glsl_prefix,
    emath_prefix,
    array,
    shader_cls,
    shader_kwargs,
    expected_uniform_count,
) -> None:
    glsl_version = "140"

    if glsl_prefix == "d":
        glsl_version = "400 core"
        if gl_version < (4, 0):
            pytest.xfail()

    if location is not None or shader_cls is ComputeShader:
        glsl_version = "430 core"
        if gl_version < (4, 3):
            pytest.xfail()

    if location is None:
        layout = ""
    else:
        layout = f"layout(location={location})"
    if array:
        array_def = "[2]"
        x_value = "uni_name[0][0][0]"
        y_value = "uni_name[1][0][0]"
    else:
        array_def = ""
        x_value = "uni_name[0][0]"
        y_value = "0"
    shader = shader_cls(
        **{
            k: v.format(
                glsl_version=glsl_version,
                layout=layout,
                glsl_prefix=glsl_prefix,
                rows=rows,
                columns=columns,
                array_def=array_def,
                x_value=x_value,
                y_value=y_value,
            ).encode("utf-8")
            for k, v in shader_kwargs.items()
        }
    )
    uni = shader["uni_name"]
    assert len(shader.uniforms) == expected_uniform_count
    assert uni in shader.uniforms
    assert isinstance(uni, ShaderUniform)
    assert uni.name == "uni_name"
    assert uni.data_type is getattr(emath, f"{emath_prefix}Matrix{rows}x{columns}")
    assert uni.size == (2 if array else 1)
    assert uni.location == (0 if location is None else location)

    python_type = getattr(emath, f"{emath_prefix}Matrix{rows}x{columns}")
    shader._activate()
    with ExitStack() as exit_stack:
        array_type = getattr(emath, python_type.__name__ + "Array")
        with pytest.raises(ValueError) as excinfo:
            shader._set_uniform(uni, None, exit_stack)
        assert (
            str(excinfo.value)
            == f"expected {python_type} or {array_type} for uni_name (got {type(None)})"
        )

        with pytest.raises(ValueError) as excinfo:
            shader._set_uniform(uni, ["1", "2"], exit_stack)
        assert (
            str(excinfo.value)
            == f"expected {python_type} or {array_type} for uni_name (got {list})"
        )

        if array:
            shader._set_uniform(
                uni,
                array_type(
                    python_type(*(25 for i in range(rows * columns))),
                    python_type(*(50 for i in range(rows * columns))),
                ),
                exit_stack,
            )
            get_value_0 = (ctypes.c_float * rows * columns)()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            for r in range(rows):
                for c in range(columns):
                    assert get_value_0[c][r] == 25
            get_value_1 = (ctypes.c_float * rows * columns)()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            for r in range(rows):
                for c in range(columns):
                    assert get_value_1[c][r] == 50

            shader._set_uniform(
                uni,
                array_type(
                    python_type(*(30 for i in range(rows * columns))),
                    python_type(*(55 for i in range(rows * columns))),
                    python_type(*(65 for i in range(rows * columns))),
                ),
                exit_stack,
            )
            get_value_0 = (ctypes.c_float * rows * columns)()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            for r in range(rows):
                for c in range(columns):
                    assert get_value_0[c][r] == 30
            get_value_1 = (ctypes.c_float * rows * columns)()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            for r in range(rows):
                for c in range(columns):
                    assert get_value_1[c][r] == 55

            shader._set_uniform(
                uni, array_type(python_type(*(40 for i in range(rows * columns)))), exit_stack
            )
            get_value_0 = (ctypes.c_float * rows * columns)()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            for r in range(rows):
                for c in range(columns):
                    assert get_value_0[c][r] == 40
            get_value_1 = (ctypes.c_float * rows * columns)()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            for r in range(rows):
                for c in range(columns):
                    assert get_value_1[c][r] == 55

            shader._set_uniform(uni, array_type(), exit_stack)
            get_value_0 = (ctypes.c_float * rows * columns)()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            for r in range(rows):
                for c in range(columns):
                    assert get_value_0[c][r] == 40
            get_value_1 = (ctypes.c_float * rows * columns)()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            for r in range(rows):
                for c in range(columns):
                    assert get_value_1[c][r] == 55

            shader._set_uniform(uni, python_type(*(44 for i in range(rows * columns))), exit_stack)
            get_value_0 = (ctypes.c_float * rows * columns)()
            glGetUniformfv(shader._gl_program, uni.location, get_value_0)
            for r in range(rows):
                for c in range(columns):
                    assert get_value_0[c][r] == 44
            get_value_1 = (ctypes.c_float * rows * columns)()
            glGetUniformfv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            for r in range(rows):
                for c in range(columns):
                    assert get_value_1[c][r] == 55
        else:
            shader._set_uniform(
                uni, python_type(*(100 for i in range(rows * columns))), exit_stack
            )
            get_value = (ctypes.c_float * rows * columns)()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            for r in range(rows):
                for c in range(columns):
                    assert get_value[c][r] == 100

            shader._set_uniform(
                uni, array_type(python_type(*(40 for i in range(rows * columns)))), exit_stack
            )
            get_value = (ctypes.c_float * rows * columns)()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            for r in range(rows):
                for c in range(columns):
                    assert get_value[c][r] == 40

            shader._set_uniform(
                uni,
                array_type(
                    python_type(*(41 for i in range(rows * columns))),
                    python_type(*(42 for i in range(rows * columns))),
                ),
                exit_stack,
            )
            get_value = (ctypes.c_float * rows * columns)()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            for r in range(rows):
                for c in range(columns):
                    assert get_value[c][r] == 41

            shader._set_uniform(uni, array_type(), exit_stack)
            get_value = (ctypes.c_float * rows * columns)()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            for r in range(rows):
                for c in range(columns):
                    assert get_value[c][r] == 41


@pytest.mark.parametrize("binding", [None, 1])
@pytest.mark.parametrize(
    "shader_cls, shader_kwargs",
    [
        (
            Shader,
            {
                "vertex": """#version 430 core
in vec2 xy;
void main()
{{
    gl_Position = vec4(xy, 0, 1);
}}
""",
                "fragment": """#version 430 core
{layout} buffer BlockName
{{
    float value;
}} block_name;
out vec4 FragColor;
void main()
{{
    FragColor = vec4(block_name.value, 0, 0, 1);
}}
""",
            },
        ),
        (
            ComputeShader,
            {
                "compute": """#version 430 core
layout (local_size_x=1, local_size_y=1, local_size_z=1) in;
{layout} buffer BlockName
{{
    float value;
}} block_name;
void main()
{{
    block_name.value = 1.0;
}}
"""
            },
        ),
    ],
)
def test_storage_block(platform, gl_version, binding, shader_cls, shader_kwargs):
    glsl_version = "430 core"
    if gl_version < (4, 3):
        pytest.xfail()

    if binding is None:
        layout = ""
    else:
        layout = f"layout(std430, binding={binding})"

    shader = shader_cls(
        **{k: v.format(layout=layout).encode("utf-8") for k, v in shader_kwargs.items()}
    )

    assert len(shader.storage_blocks) == 1
    storage_block = shader.storage_blocks[0]
    assert isinstance(storage_block, ShaderStorageBlock)
    assert storage_block.name == "BlockName"

    g_buffer = GBuffer(ctypes.sizeof(ctypes.c_float))
    with ExitStack() as exit_stack:
        shader._set_storage_block(storage_block, g_buffer, exit_stack)

        assert g_buffer._shader_storage_buffer_unit is not None
        binding_value = ctypes.c_int()
        glGetIntegeri_v(
            GL_SHADER_STORAGE_BUFFER_BINDING,
            g_buffer._shader_storage_buffer_unit,
            ctypes.byref(binding_value),
        )
        assert binding_value.value == g_buffer._gl_buffer
