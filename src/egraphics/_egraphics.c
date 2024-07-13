
#include "GL/glew.h"

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdio.h>

#define CHECK_UNEXPECTED_ARG_COUNT_ERROR(expected_count)\
    if (expected_count != nargs)\
    {\
        PyErr_Format(PyExc_TypeError, "expected %z args, got %z", expected_count, nargs);\
        return 0;\
    }

#define CHECK_UNEXPECTED_PYTHON_ERROR()\
    if (PyErr_Occurred())\
    {\
        return 0;\
    }

#define CHECK_GL_ERROR()\
    {\
        GLenum gl_error = glGetError();\
        if (gl_error != GL_NO_ERROR)\
        {\
            PyErr_Format(PyExc_RuntimeError, "gl error: %s", gluErrorString(gl_error));\
            return 0;\
        }\
    }

static PyObject *
bind_gl_buffer(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    GLenum target = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    GLuint gl_buffer = 0;
    if (args[1] != Py_None)
    {
        gl_buffer = PyLong_AsLong(args[1]);
        CHECK_UNEXPECTED_PYTHON_ERROR();
    }

    glBindBuffer(target, gl_buffer);
    CHECK_GL_ERROR();

    Py_RETURN_NONE;
}

static PyObject *
create_gl_buffer(PyObject *module, PyObject *unused)
{
    GLuint gl_buffer = 0;

    glGenBuffers(1, &gl_buffer);
    CHECK_GL_ERROR();

    return PyLong_FromUnsignedLong(gl_buffer);
}

static PyObject *
delete_gl_buffer(PyObject *module, PyObject *py_gl_buffer)
{
    GLuint gl_buffer = PyLong_AsLong(py_gl_buffer);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    glDeleteBuffers(1, &gl_buffer);

    Py_RETURN_NONE;
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
            return 0;
        }
        buffer.len = length;
        buffer.buf = 0;
    }
    else
    {
        if (PyObject_GetBuffer(data, &buffer, PyBUF_CONTIG_RO) == -1){ return 0; }
    }

    glBufferData(target, buffer.len, buffer.buf, usage);

    if (buffer.buf != 0)
    {
        PyBuffer_Release(&buffer);
    }

    CHECK_GL_ERROR();

    return PyLong_FromSsize_t(buffer.len);
}

static PyMethodDef module_PyMethodDef[] = {
    {"create_gl_buffer", create_gl_buffer, METH_NOARGS, 0},
    {"delete_gl_buffer", delete_gl_buffer, METH_O, 0},
    {"bind_gl_buffer", (PyCFunction)bind_gl_buffer, METH_FASTCALL, 0},
    {"set_gl_buffer_target_data", (PyCFunction)set_gl_buffer_target_data, METH_FASTCALL, 0},
    {0},
};

static struct PyModuleDef module_PyModuleDef = {
    PyModuleDef_HEAD_INIT,
    "egraphics._egraphics",
    0,
    -1,
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

    ADD_CONSTANT(GL_STREAM_DRAW);
    ADD_CONSTANT(GL_STREAM_READ);
    ADD_CONSTANT(GL_STREAM_COPY);
    ADD_CONSTANT(GL_STATIC_DRAW);
    ADD_CONSTANT(GL_STATIC_READ);
    ADD_CONSTANT(GL_STATIC_COPY);
    ADD_CONSTANT(GL_DYNAMIC_DRAW);
    ADD_CONSTANT(GL_DYNAMIC_READ);
    ADD_CONSTANT(GL_DYNAMIC_COPY);

    return module;
}