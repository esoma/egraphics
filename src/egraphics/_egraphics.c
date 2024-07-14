
#include "GL/glew.h"

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

#include "emath.h"

#define CHECK_UNEXPECTED_ARG_COUNT_ERROR(expected_count)\
    if (expected_count != nargs)\
    {\
        PyErr_Format(PyExc_TypeError, "expected %z args, got %z", expected_count, nargs);\
        goto error;\
    }

#define CHECK_UNEXPECTED_PYTHON_ERROR()\
    if (PyErr_Occurred())\
    {\
        goto error;\
    }

#define CHECK_GL_ERROR()\
    {\
        GLenum gl_error = glGetError();\
        if (gl_error != GL_NO_ERROR)\
        {\
            PyErr_Format(PyExc_RuntimeError, "gl error: %s", gluErrorString(gl_error));\
            goto error;\
        }\
    }

typedef struct ModuleState
{
    float clear_color[3];
    float clear_depth;
} ModuleState;

static PyObject *
reset_module_state(PyObject *module, PyObject *unused)
{
    ModuleState *state = (ModuleState *)PyModule_GetState(module);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    state->clear_color[0] = -1;
    state->clear_color[1] = -1;
    state->clear_color[2] = -1;
    state->clear_depth = -1;

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
activate_gl_vertex_array(PyObject *module, PyObject *py_gl_vertex_array)
{
    GLuint gl_vertex_array = 0;
    if (py_gl_vertex_array != Py_None)
    {
        gl_vertex_array = PyLong_AsLong(py_gl_vertex_array);
        CHECK_UNEXPECTED_PYTHON_ERROR();
    }

    glBindVertexArray(gl_vertex_array);
    CHECK_GL_ERROR();

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_gl_buffer_target(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    GLenum target = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    GLuint gl_buffer = 0;
    if (args[1] != Py_None)
    {
        gl_buffer = PyLong_AsUnsignedLong(args[1]);
        CHECK_UNEXPECTED_PYTHON_ERROR();
    }

    glBindBuffer(target, gl_buffer);
    CHECK_GL_ERROR();

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
create_gl_buffer(PyObject *module, PyObject *unused)
{
    GLuint gl_buffer = 0;

    glGenBuffers(1, &gl_buffer);
    CHECK_GL_ERROR();

    return PyLong_FromUnsignedLong(gl_buffer);
error:
    return 0;
}

static PyObject *
create_gl_vertex_array(PyObject *module, PyObject *unused)
{
    GLuint gl_vertex_array = 0;

    glGenVertexArrays(1, &gl_vertex_array);
    CHECK_GL_ERROR();

    return PyLong_FromUnsignedLong(gl_vertex_array);
error:
    return 0;
}

static PyObject *
create_gl_texture(PyObject *module, PyObject *unused)
{
    GLuint gl_texture = 0;

    glGenTextures(1, &gl_texture);
    CHECK_GL_ERROR();

    return PyLong_FromUnsignedLong(gl_texture);
error:
    return 0;
}

static PyObject *
delete_gl_buffer(PyObject *module, PyObject *py_gl_buffer)
{
    GLuint gl_buffer = PyLong_AsUnsignedLong(py_gl_buffer);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    glDeleteBuffers(1, &gl_buffer);

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
delete_gl_vertex_array(PyObject *module, PyObject *py_gl_vertex_array)
{
    GLuint gl_vertex_array = PyLong_AsUnsignedLong(py_gl_vertex_array);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    glDeleteVertexArrays(1, &gl_vertex_array);

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
delete_gl_texture(PyObject *module, PyObject *py_gl_texture)
{
    GLuint gl_texture = PyLong_AsUnsignedLong(py_gl_texture);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    glDeleteTextures(1, &gl_texture);

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_gl_buffer_target_data(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(3);

    GLenum target = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    PyObject *data = args[1];

    GLenum usage = PyLong_AsLong(args[2]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    Py_buffer buffer;
    if (PyLong_Check(data))
    {
        long length = PyLong_AsLong(data);
        CHECK_UNEXPECTED_PYTHON_ERROR();
        if (length < 0)
        {
            PyErr_Format(PyExc_ValueError, "data must be 0 or more");
            goto error;
        }
        buffer.len = length;
        buffer.buf = 0;
    }
    else
    {
        if (PyObject_GetBuffer(data, &buffer, PyBUF_CONTIG_RO) == -1){ goto error; }
    }

    glBufferData(target, buffer.len, buffer.buf, usage);

    if (buffer.buf != 0)
    {
        PyBuffer_Release(&buffer);
    }

    CHECK_GL_ERROR();

    return PyLong_FromSsize_t(buffer.len);
error:
    return 0;
}

static PyObject *
create_gl_buffer_memory_view(PyObject *module, PyObject *py_length)
{
    Py_ssize_t length = PyLong_AsSsize_t(py_length);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    void *memory = glMapBuffer(GL_COPY_READ_BUFFER, GL_READ_WRITE);
    CHECK_GL_ERROR();

    PyObject *memory_view = PyMemoryView_FromMemory(memory, length, PyBUF_WRITE);
    if (!memory_view)
    {
        glUnmapBuffer(GL_COPY_READ_BUFFER);
        CHECK_GL_ERROR();
        goto error;
    }

    return memory_view;
error:
    return 0;
}

static PyObject *
release_gl_copy_read_buffer_memory_view(PyObject *module, PyObject *unused)
{
    glUnmapBuffer(GL_COPY_READ_BUFFER);
    CHECK_GL_ERROR();
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
configure_gl_vertex_array_location(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(6);

    GLuint location = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    GLint count = PyLong_AsLong(args[1]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    GLenum type = PyLong_AsLong(args[2]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    GLsizei stride = PyLong_AsLong(args[3]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    void *offset = (void *)PyLong_AsLong(args[4]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    PyObject *py_instancing_divisor = args[5];

    glVertexAttribPointer(location, count, type, GL_FALSE, stride, offset);
    CHECK_GL_ERROR();

    glEnableVertexAttribArray(location);
    CHECK_GL_ERROR();

    if (py_instancing_divisor == Py_None)
    {
        GLuint instancing_divisor = PyLong_AsLong(py_instancing_divisor);
        CHECK_UNEXPECTED_PYTHON_ERROR();
        glVertexAttribDivisor(location, instancing_divisor);
        CHECK_GL_ERROR();
    }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_read_framebuffer(PyObject *module, PyObject *unused)
{
    glBindFramebuffer(GL_READ_FRAMEBUFFER, 0);
    CHECK_GL_ERROR();

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
read_color_from_framebuffer(PyObject *module, PyObject *rect)
{
    struct EMathApi *emath_api = 0;

    PyObject *py_position = PyObject_GetAttrString(rect, "position");
    CHECK_UNEXPECTED_PYTHON_ERROR();

    PyObject *py_size = PyObject_GetAttrString(rect, "size");
    CHECK_UNEXPECTED_PYTHON_ERROR();

    emath_api = EMathApi_Get();
    CHECK_UNEXPECTED_PYTHON_ERROR();

    const int *position = emath_api->IVector2_GetValuePointer(py_position);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    const int *size = emath_api->IVector2_GetValuePointer(py_size);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    size_t count = (size_t)size[0] * (size_t)size[1];
    float *data = malloc(sizeof(float) * 4 * count);
    if (!data)
    {
        PyErr_Format(PyExc_MemoryError, "out of memory");
        goto error;
    }

    glReadPixels(position[0], position[1], size[0], size[1], GL_RGBA, GL_FLOAT, data);
    CHECK_GL_ERROR();

    PyObject *array = emath_api->FVector4Array_Create(count, data);
    free(data);
    EMathApi_Release();
    return array;
error:
    PyObject *ex = PyErr_GetRaisedException();
    if (emath_api){ EMathApi_Release(); }
    PyErr_SetRaisedException(ex);
    return 0;
}

static PyObject *
read_depth_from_framebuffer(PyObject *module, PyObject *rect)
{
    struct EMathApi *emath_api = 0;

    PyObject *py_position = PyObject_GetAttrString(rect, "position");
    CHECK_UNEXPECTED_PYTHON_ERROR();

    PyObject *py_size = PyObject_GetAttrString(rect, "size");
    CHECK_UNEXPECTED_PYTHON_ERROR();

    emath_api = EMathApi_Get();
    CHECK_UNEXPECTED_PYTHON_ERROR();

    const int *position = emath_api->IVector2_GetValuePointer(py_position);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    const int *size = emath_api->IVector2_GetValuePointer(py_size);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    size_t count = (size_t)size[0] * (size_t)size[1];
    float *data = malloc(sizeof(float) * count);
    if (!data)
    {
        PyErr_Format(PyExc_MemoryError, "out of memory");
        goto error;
    }

    glReadPixels(position[0], position[1], size[0], size[1], GL_DEPTH_COMPONENT, GL_FLOAT, data);
    CHECK_GL_ERROR();

    PyObject *array = emath_api->FArray_Create(count, data);
    free(data);
    EMathApi_Release();
    return array;
error:
    PyObject *ex = PyErr_GetRaisedException();
    if (emath_api){ EMathApi_Release(); }
    PyErr_SetRaisedException(ex);
    return 0;
}

static PyObject *
clear_framebuffer(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    struct EMathApi *emath_api = 0;

    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    PyObject *py_color = args[0];
    PyObject *py_depth = args[1];

    GLbitfield clear_mask = 0;

    ModuleState *state = (ModuleState *)PyModule_GetState(module);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    if (py_color != Py_None)
    {
        emath_api = EMathApi_Get();
        CHECK_UNEXPECTED_PYTHON_ERROR();

        const float *color = emath_api->FVector3_GetValuePointer(py_color);
        CHECK_UNEXPECTED_PYTHON_ERROR();

        EMathApi_Release();

        if (memcmp(state->clear_color, color, sizeof(float) * 3) != 0)
        {
            glClearColor(color[0], color[1], color[2], 1.0);
            CHECK_GL_ERROR();
            memcpy(state->clear_color, color, sizeof(float) * 3);
        }
        clear_mask |= GL_COLOR_BUFFER_BIT;
    }

    if (py_depth != Py_None)
    {
        float depth = PyFloat_AsDouble(py_depth);
        CHECK_UNEXPECTED_PYTHON_ERROR();
        if (depth != state->clear_depth)
        {
            glClearDepth(depth);
            CHECK_GL_ERROR();
        }
        clear_mask |= GL_DEPTH_BUFFER_BIT;
    }

    if (clear_mask != 0)
    {
        glClear(clear_mask);
        CHECK_GL_ERROR();
    }
    Py_RETURN_NONE;
error:
    PyObject *ex = PyErr_GetRaisedException();
    if (emath_api){ EMathApi_Release(); }
    PyErr_SetRaisedException(ex);
    return 0;
}

static PyObject *
set_active_gl_texture_unit(PyObject *module, PyObject *py_unit)
{
    GLenum unit = PyLong_AsLong(py_unit);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    glActiveTexture(GL_TEXTURE0 + unit);
    CHECK_GL_ERROR();

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_gl_texture_target(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    GLenum target = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    GLuint gl_texture = 0;
    if (args[1] != Py_None)
    {
        gl_texture = PyLong_AsUnsignedLong(args[1]);
        CHECK_UNEXPECTED_PYTHON_ERROR();
    }

    glBindTexture(target, gl_texture);
    CHECK_GL_ERROR();

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_gl_texture_target_2d_data(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    struct EMathApi *emath_api = 0;

    CHECK_UNEXPECTED_ARG_COUNT_ERROR(5);

    GLenum target = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    GLint format = PyLong_AsLong(args[1]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    GLsizei width = 0;
    GLsizei height = 0;
    {
        PyObject *py_size = args[2];

        emath_api = EMathApi_Get();
        CHECK_UNEXPECTED_PYTHON_ERROR();

        const unsigned int *size = emath_api->UVector2_GetValuePointer(py_size);
        CHECK_UNEXPECTED_PYTHON_ERROR();

        EMathApi_Release();

        width = size[0];
        height = size[1];
    }

    GLenum type = PyLong_AsLong(args[3]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    Py_buffer buffer;
    {
        PyObject *py_data = args[4];
        if (PyObject_GetBuffer(py_data, &buffer, PyBUF_CONTIG_RO) == -1){ goto error; }
    }

    glTexImage2D(
        target,
        0,
        format,
        width,
        height,
        0,
        format,
        type,
        buffer.buf
    );
    PyBuffer_Release(&buffer);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    CHECK_GL_ERROR();

    Py_RETURN_NONE;
error:
    PyObject *ex = PyErr_GetRaisedException();
    if (emath_api){ EMathApi_Release(); }
    PyErr_SetRaisedException(ex);
    return 0;
}

static PyObject *
generate_gl_texture_target_mipmaps(PyObject *module, PyObject *py_target)
{
    GLenum target = PyLong_AsLong(py_target);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    glGenerateMipmap(target);
    CHECK_GL_ERROR();

    Py_RETURN_NONE;
error:
    return 0;
}


static PyObject *
set_gl_texture_target_parameters(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(6);

    GLenum target = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    GLenum min_filter = PyLong_AsLong(args[1]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    GLenum mag_filter = PyLong_AsLong(args[2]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    glTexParameteri(target, GL_TEXTURE_MIN_FILTER, min_filter);
    CHECK_GL_ERROR();

    glTexParameteri(target, GL_TEXTURE_MAG_FILTER, mag_filter);
    CHECK_GL_ERROR();

    for (size_t i = 0; i < 3; i++)
    {
        static const GLenum wrap_target[] = {
            GL_TEXTURE_WRAP_S,
            GL_TEXTURE_WRAP_T,
            GL_TEXTURE_WRAP_R
        };
        PyObject *py_wrap = args[3 + i];
        if (i > 0 && py_wrap == Py_None){ break; }
        GLenum wrap = PyLong_AsLong(py_wrap);
        CHECK_UNEXPECTED_PYTHON_ERROR();

        glTexParameteri(target, wrap_target[i], wrap);
        CHECK_GL_ERROR();
    }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyMethodDef module_PyMethodDef[] = {
    {"reset_module_state", reset_module_state, METH_NOARGS, 0},
    {"activate_gl_vertex_array", activate_gl_vertex_array, METH_O, 0},
    {"create_gl_buffer", create_gl_buffer, METH_NOARGS, 0},
    {"create_gl_vertex_array", create_gl_vertex_array, METH_NOARGS, 0},
    {"create_gl_texture", create_gl_texture, METH_NOARGS, 0},
    {"delete_gl_buffer", delete_gl_buffer, METH_O, 0},
    {"delete_gl_vertex_array", delete_gl_vertex_array, METH_O, 0},
    {"delete_gl_texture", delete_gl_texture, METH_O, 0},
    {"set_gl_buffer_target", (PyCFunction)set_gl_buffer_target, METH_FASTCALL, 0},
    {"set_gl_buffer_target_data", (PyCFunction)set_gl_buffer_target_data, METH_FASTCALL, 0},
    {"create_gl_copy_read_buffer_memory_view", create_gl_buffer_memory_view, METH_O, 0},
    {"release_gl_copy_read_buffer_memory_view", release_gl_copy_read_buffer_memory_view, METH_NOARGS, 0},
    {"configure_gl_vertex_array_location", (PyCFunction)configure_gl_vertex_array_location, METH_FASTCALL, 0},
    {"set_read_framebuffer", set_read_framebuffer, METH_NOARGS, 0},
    {"read_color_from_framebuffer", read_color_from_framebuffer, METH_O, 0},
    {"read_depth_from_framebuffer", read_depth_from_framebuffer, METH_O, 0},
    {"clear_framebuffer", (PyCFunction)clear_framebuffer, METH_FASTCALL, 0},
    {"set_active_gl_texture_unit", set_active_gl_texture_unit, METH_O, 0},
    {"set_gl_texture_target", (PyCFunction)set_gl_texture_target, METH_FASTCALL, 0},
    {"set_gl_texture_target_2d_data", (PyCFunction)set_gl_texture_target_2d_data, METH_FASTCALL, 0},
    {"generate_gl_texture_target_mipmaps", generate_gl_texture_target_mipmaps, METH_O, 0},
    {"set_gl_texture_target_parameters", (PyCFunction)set_gl_texture_target_parameters, METH_FASTCALL, 0},
    {0},
};

static struct PyModuleDef module_PyModuleDef = {
    PyModuleDef_HEAD_INIT,
    "egraphics._egraphics",
    0,
    sizeof(ModuleState),
    module_PyMethodDef,
};

PyMODINIT_FUNC
PyInit__egraphics()
{
    {
        PyObject *eplatform = PyImport_ImportModule("eplatform");
        if (!eplatform){ return 0; }

        PyObject *platform_cls = PyObject_GetAttrString(eplatform, "Platform");
        Py_DECREF(eplatform);
        if (!platform_cls){ return 0; }

        PyObject *platform = PyObject_CallNoArgs(platform_cls);
        Py_DECREF(platform_cls);
        if (!platform){ return 0; }

        PyObject *context = PyObject_CallMethod(platform, "__enter__", "");
        Py_XDECREF(context);
        if (!context)
        {
            Py_DECREF(platform);
            return 0;
        }

        GLenum err = glewInit();
        if (err != GLEW_OK)
        {
            Py_XDECREF(PyObject_CallMethod(platform, "__exit__", ""));
            Py_DECREF(platform);
            PyErr_SetString(PyExc_RuntimeError, glewGetErrorString(err));
            return 0;
        }

        context = PyObject_CallMethod(platform, "__exit__", "");
        Py_XDECREF(context);
        Py_DECREF(platform);
        if (!context){ return 0; }
    }

    PyObject *module = PyModule_Create(&module_PyModuleDef);
    if (!module){ return 0; }

    if (PyState_AddModule(module, &module_PyModuleDef) == -1)
    {
        Py_DECREF(module);
        return 0;
    }
    {
        PyObject *r = reset_module_state(module, 0);
        if (!r)
        {
            Py_DECREF(module);
            return 0;
        }
        Py_DECREF(r);
    }

#define ADD_ALIAS(name, type)\
    {\
        if (PyModule_AddObjectRef(module, name, (PyObject *)&type) != 0)\
        {\
            return 0;\
        }\
    }

    ADD_ALIAS("GlBuffer", PyLong_Type);
    ADD_ALIAS("GlBufferTarget", PyLong_Type);
    ADD_ALIAS("GlBufferUsage", PyLong_Type);
    ADD_ALIAS("GlVertexArray", PyLong_Type);
    ADD_ALIAS("GlType", PyLong_Type);
    ADD_ALIAS("GlTexture", PyLong_Type);
    ADD_ALIAS("GlTextureComponents", PyLong_Type);
    ADD_ALIAS("GlTextureFilter", PyLong_Type);
    ADD_ALIAS("GlTextureTarget", PyLong_Type);
    ADD_ALIAS("GlTexturWrap", PyLong_Type);

#define ADD_CONSTANT(n)\
    {\
        PyObject *constant = PyLong_FromLong(n);\
        if (!constant){ return 0; }\
        if (PyModule_AddObject(module, #n, constant) != 0)\
        {\
            Py_DECREF(constant);\
            return 0;\
        }\
    }

    ADD_CONSTANT(GL_ARRAY_BUFFER);
    ADD_CONSTANT(GL_COPY_READ_BUFFER);
    ADD_CONSTANT(GL_ELEMENT_ARRAY_BUFFER);

    ADD_CONSTANT(GL_STREAM_DRAW);
    ADD_CONSTANT(GL_STREAM_READ);
    ADD_CONSTANT(GL_STREAM_COPY);
    ADD_CONSTANT(GL_STATIC_DRAW);
    ADD_CONSTANT(GL_STATIC_READ);
    ADD_CONSTANT(GL_STATIC_COPY);
    ADD_CONSTANT(GL_DYNAMIC_DRAW);
    ADD_CONSTANT(GL_DYNAMIC_READ);
    ADD_CONSTANT(GL_DYNAMIC_COPY);

    ADD_CONSTANT(GL_FLOAT);
    ADD_CONSTANT(GL_DOUBLE);
    ADD_CONSTANT(GL_BYTE);
    ADD_CONSTANT(GL_UNSIGNED_BYTE);
    ADD_CONSTANT(GL_SHORT);
    ADD_CONSTANT(GL_UNSIGNED_SHORT);
    ADD_CONSTANT(GL_INT);
    ADD_CONSTANT(GL_UNSIGNED_INT);

    ADD_CONSTANT(GL_RED);
    ADD_CONSTANT(GL_RG);
    ADD_CONSTANT(GL_RGB);
    ADD_CONSTANT(GL_RGBA);

    ADD_CONSTANT(GL_CLAMP_TO_EDGE);
    ADD_CONSTANT(GL_CLAMP_TO_BORDER);
    ADD_CONSTANT(GL_REPEAT);
    ADD_CONSTANT(GL_MIRRORED_REPEAT);
    ADD_CONSTANT(GL_MIRROR_CLAMP_TO_EDGE);

    ADD_CONSTANT(GL_NEAREST);
    ADD_CONSTANT(GL_LINEAR);
    ADD_CONSTANT(GL_NEAREST_MIPMAP_NEAREST);
    ADD_CONSTANT(GL_NEAREST_MIPMAP_LINEAR);
    ADD_CONSTANT(GL_LINEAR_MIPMAP_NEAREST);
    ADD_CONSTANT(GL_LINEAR_MIPMAP_LINEAR);

    ADD_CONSTANT(GL_TEXTURE_2D);

    {
        PyObject *eplatform = PyImport_ImportModule("eplatform");
        if (!eplatform){ return 0; }

        PyObject *platform_cls = PyObject_GetAttrString(eplatform, "Platform");
        Py_DECREF(eplatform);
        if (!platform_cls){ return 0; }

        PyObject *py_reset_module_state = PyObject_GetAttrString(module, "reset_module_state");
        if (!py_reset_module_state)
        {
            Py_DECREF(platform_cls);
            return 0;
        }

        PyObject *r = PyObject_CallMethod(
            platform_cls, "register_deactivate_callback", "O", py_reset_module_state
        );
        Py_DECREF(platform_cls);
        Py_DECREF(py_reset_module_state);
        if (!r){ return 0; }
        Py_DECREF(r);
    }

    return module;
}