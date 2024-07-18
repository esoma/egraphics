# egraphics
from egraphics import Shader
from egraphics import ShaderAttribute
from egraphics import ShaderUniform
from egraphics import Texture
from egraphics import Texture2d
from egraphics import TextureComponents

# emath
import emath
from emath import DArray
from emath import FArray
from emath import I32Array
from emath import U8Array
from emath import U32Array
from emath import UVector2

# pyopengl
from OpenGL.GL import glGetUniformLocation
from OpenGL.GL import glGetUniformfv
from OpenGL.GL import glGetUniformiv
from OpenGL.GL import glIsProgram

# pytest
import pytest

# python
from contextlib import ExitStack
import ctypes
import sys


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
            """.encode(
                "utf-8"
            )
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
    """.encode(
            "utf-8"
        )
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
def test_pod_uniforms(platform, gl_version, location, glsl_type, python_type, array_type, array):
    glsl_version = "140"

    if glsl_type == "double":
        glsl_version = "400 core"
        if gl_version < (4, 0):
            pytest.xfail()

    if location is not None:
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
    shader = Shader(
        vertex=f"""#version {glsl_version}
    {layout} uniform {glsl_type} uni_name{array_def};
    void main()
    {{
        gl_Position = vec4({x_value}, {y_value}, 0, 1);
    }}
    """.encode(
            "utf-8"
        )
    )
    uni = shader["uni_name"]
    assert len(shader.uniforms) == 1
    assert shader.uniforms[0] is uni
    assert isinstance(uni, ShaderUniform)
    assert uni.name == "uni_name"
    assert uni.data_type is python_type
    assert uni.size == (2 if array else 1)
    assert uni.location == (0 if location is None else location)

    shader._activate()
    with ExitStack() as exit_stack:
        if array:
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, None, exit_stack)
            assert str(excinfo.value) == f"expected {array_type} for uni_name (got {type(None)})"
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, U8Array(0, 1), exit_stack)
            assert str(excinfo.value) == f"expected {array_type} for uni_name (got {U8Array})"
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, array_type(0), exit_stack)
            assert str(excinfo.value) == (
                f"expected array of length 2 for uni_name " f"(got array of length 1)"
            )
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
        else:
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, None, exit_stack)
            assert str(excinfo.value) == f"expected {python_type} for uni_name (got {type(None)})"
            shader._set_uniform(uni, python_type(1), exit_stack)

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
def test_sampler_uniforms(platform, gl_version, location, prefix, postfix, components, array):
    glsl_version = "140"

    if postfix in ["2DMS", "2DMSArray"]:
        glsl_version = "150"
        if gl_version < (3, 2):
            pytest.xfail()

    if postfix == "CubeArray":
        glsl_version = "400 core"
        if gl_version < (4, 0):
            pytest.xfail()

    if location is not None:
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
    shader = Shader(
        vertex=f"""#version {glsl_version}
    {layout} uniform {prefix}sampler{postfix} uni_name{array_def};
    void main()
    {{
        gl_Position = vec4({x_value}, {y_value}, 0, 1);
    }}
    """.encode(
            "utf-8"
        )
    )
    uni = shader["uni_name"]
    assert len(shader.uniforms) == 1
    assert shader.uniforms[0] is uni
    assert isinstance(uni, ShaderUniform)
    assert uni.name == "uni_name"
    assert uni.data_type is Texture
    assert uni.size == (2 if array else 1)
    assert uni.location == (0 if location is None else location)

    shader._activate()
    with ExitStack() as exit_stack:
        if array:
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, None, exit_stack)
            assert str(excinfo.value) == (
                f"expected sequence of {Texture} for uni_name (got {type(None)})"
            )
            bad_value = ["1", "2"]
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, bad_value, exit_stack)
            assert str(excinfo.value) == (
                f"expected sequence of {Texture} for uni_name " f"(got {bad_value!r})"
            )
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, I32Array(0), exit_stack)
            assert str(excinfo.value) == (
                f"expected sequence of length 2 for uni_name " f"(got sequence of length 1)"
            )
            tex1 = Texture2d(UVector2(1, 1), TextureComponents.R, ctypes.c_uint8, b"\x00")
            tex2 = Texture2d(UVector2(1, 1), TextureComponents.R, ctypes.c_uint8, b"\x00")
            shader._set_uniform(uni, [tex1, tex2], exit_stack)

            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex1._unit
            assert get_value_1.value == tex2._unit
        else:
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, None, exit_stack)
            assert str(excinfo.value) == (f"expected {Texture} for uni_name (got {type(None)})")
            tex = Texture2d(UVector2(1, 1), TextureComponents.R, ctypes.c_uint8, b"\x00")
            shader._set_uniform(uni, tex, exit_stack)

            get_value = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value)
            assert get_value.value == tex._unit


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
def test_shadow_sampler_uniforms(
    platform,
    gl_version,
    location,
    postfix,
    components,
    array,
):
    glsl_version = "140"

    if location is not None:
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
    shader = Shader(
        vertex=f"""#version {glsl_version}
    {layout} uniform sampler{postfix} uni_name{array_def};
    void main()
    {{
        gl_Position = vec4({x_value}, {y_value}, 0, 1);
    }}
    """.encode(
            "utf-8"
        )
    )
    uni = shader["uni_name"]
    assert len(shader.uniforms) == 1
    assert shader.uniforms[0] is uni
    assert isinstance(uni, ShaderUniform)
    assert uni.name == "uni_name"
    assert uni.data_type is Texture
    assert uni.size == (2 if array else 1)
    assert uni.location == (0 if location is None else location)

    shader._activate()
    with ExitStack() as exit_stack:
        if array:
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, None, exit_stack)
            assert str(excinfo.value) == (
                f"expected sequence of {Texture} for uni_name (got {type(None)})"
            )
            bad_value = ["1", "2"]
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, bad_value, exit_stack)
            assert str(excinfo.value) == (
                f"expected sequence of {Texture} for uni_name " f"(got {bad_value!r})"
            )
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, I32Array(0), exit_stack)
            assert str(excinfo.value) == (
                f"expected sequence of length 2 for uni_name " f"(got sequence of length 1)"
            )
            tex1 = Texture2d(UVector2(1, 1), TextureComponents.R, ctypes.c_uint8, b"\x00")
            tex2 = Texture2d(UVector2(1, 1), TextureComponents.R, ctypes.c_uint8, b"\x00")
            shader._set_uniform(uni, [tex1, tex2], exit_stack)

            get_value_0 = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value_0)
            get_value_1 = ctypes.c_int32()
            glGetUniformiv(
                shader._gl_program,
                glGetUniformLocation(shader._gl_program, "uni_name[1]"),
                get_value_1,
            )
            assert get_value_0.value == tex1._unit
            assert get_value_1.value == tex2._unit
        else:
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, None, exit_stack)
            assert str(excinfo.value) == (f"expected {Texture} for uni_name (got {type(None)})")
            tex = Texture2d(UVector2(1, 1), TextureComponents.R, ctypes.c_uint8, b"\x00")
            shader._set_uniform(uni, tex, exit_stack)

            get_value = ctypes.c_int32()
            glGetUniformiv(shader._gl_program, uni.location, get_value)
            assert get_value.value == tex._unit


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
    """.encode(
            "utf-8"
        )
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
def test_vector_uniforms(
    platform,
    gl_version,
    location,
    components,
    glsl_prefix,
    emath_prefix,
    array,
):
    glsl_version = "140"

    if glsl_prefix == "d":
        glsl_version = "400 core"
        if gl_version < (4, 0):
            pytest.xfail()

    if location is not None:
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
    shader = Shader(
        vertex=f"""#version {glsl_version}
    {layout} uniform {glsl_prefix}vec{components} uni_name{array_def};
    void main()
    {{
        gl_Position = vec4({x_value}, {y_value}, 0, 1);
    }}
    """.encode(
            "utf-8"
        )
    )
    uni = shader["uni_name"]
    assert len(shader.uniforms) == 1
    assert shader.uniforms[0] is uni
    assert isinstance(uni, ShaderUniform)
    assert uni.name == "uni_name"
    assert uni.data_type is getattr(emath, f"{emath_prefix}Vector{components}")
    assert uni.size == (2 if array else 1)
    assert uni.location == (0 if location is None else location)

    python_type = getattr(emath, f"{emath_prefix}Vector{components}")
    shader._activate()
    with ExitStack() as exit_stack:
        if array:
            array_type = getattr(emath, python_type.__name__ + "Array")
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, None, exit_stack)
            assert str(excinfo.value) == (f"expected {array_type} for uni_name (got {type(None)})")
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, U8Array(0, 100), exit_stack)
            assert str(excinfo.value) == (f"expected {array_type} for uni_name (got {U8Array})")
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, array_type(python_type(25)), exit_stack)
            assert str(excinfo.value) == (
                f"expected array of length 2 for uni_name " f"(got array of length 1)"
            )
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
        else:
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, None, exit_stack)
            assert str(excinfo.value) == (
                f"expected {python_type} for uni_name (got {type(None)})"
            )
            shader._set_uniform(uni, python_type(100), exit_stack)

            get_value = (ctypes.c_float * components)()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            for i in range(components):
                assert get_value[i] == 100


@pytest.mark.parametrize("location", [None, 1])
@pytest.mark.parametrize("rows", [2, 3, 4])
@pytest.mark.parametrize("columns", [2, 3, 4])
@pytest.mark.parametrize(
    "glsl_prefix, emath_prefix",
    [
        ("", "F"),
        ("d", "D"),
    ],
)
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
    """.encode(
            "utf-8"
        )
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
@pytest.mark.parametrize(
    "glsl_prefix, emath_prefix",
    [
        ("", "F"),
        ("d", "D"),
    ],
)
@pytest.mark.parametrize("array", [False, True])
def test_matrix_uniforms(
    platform,
    gl_version,
    location,
    rows,
    columns,
    glsl_prefix,
    emath_prefix,
    array,
) -> None:
    glsl_version = "140"

    if glsl_prefix == "d":
        glsl_version = "400 core"
        if gl_version < (4, 0):
            pytest.xfail()

    if location is not None:
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
    shader = Shader(
        vertex=f"""#version {glsl_version}
    {layout} uniform {glsl_prefix}mat{rows}x{columns} uni_name{array_def};
    void main()
    {{
        gl_Position = vec4({x_value}, {y_value}, 0, 1);
    }}
    """.encode(
            "utf-8"
        )
    )
    uni = shader["uni_name"]
    assert len(shader.uniforms) == 1
    assert shader.uniforms[0] is uni
    assert isinstance(uni, ShaderUniform)
    assert uni.name == "uni_name"
    assert uni.data_type is getattr(emath, f"{emath_prefix}Matrix{rows}x{columns}")
    assert uni.size == (2 if array else 1)
    assert uni.location == (0 if location is None else location)

    python_type = getattr(emath, f"{emath_prefix}Matrix{rows}x{columns}")
    shader._activate()
    with ExitStack() as exit_stack:
        if array:
            array_type = getattr(emath, python_type.__name__ + "Array")
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, None, exit_stack)
            assert str(excinfo.value) == (f"expected {array_type} for uni_name (got {type(None)})")
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, U8Array(0, 100), exit_stack)
            assert str(excinfo.value) == (f"expected {array_type} for uni_name (got {U8Array})")
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, array_type(python_type(25)), exit_stack)
            assert str(excinfo.value) == (
                f"expected array of length 2 for uni_name " f"(got array of length 1)"
            )
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
        else:
            with pytest.raises(ValueError) as excinfo:
                shader._set_uniform(uni, None, exit_stack)
            assert str(excinfo.value) == (
                f"expected {python_type} for uni_name (got {type(None)})"
            )
            shader._set_uniform(
                uni, python_type(*(100 for i in range(rows * columns))), exit_stack
            )

            get_value = (ctypes.c_float * rows * columns)()
            glGetUniformfv(shader._gl_program, uni.location, get_value)
            for r in range(rows):
                for c in range(columns):
                    assert get_value[c][r] == 100
