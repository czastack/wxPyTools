#pragma once
#include <pybind11/pybind11.h>

namespace py = pybind11;
using pyobj = py::object;
using pycref = const py::object&;

inline auto PyBytesGetBuff(const py::bytes& b)
{
	return PyBytes_AsString(b.ptr());
}


template<class T>
void vectoyExtendList(std::vector<T>& array, pycref items)
{
	if (!items.is_none())
	{
		for (auto& item : items) {
			array.emplace_back(item.cast<T>());
		}
	}
}


template <typename... Args>
py::object PyCall(const py::object& obj, Args &&...args) {
	try {
		return obj(std::forward<Args>(args)...);
	}
	catch (py::error_already_set& e)
	{
		e.restore();
		PyErr_Print();
		return py::none();
	}
}


#define PyIterable_Check(obj) \
    ((obj)->ob_type->tp_iter != NULL && \
     (obj)->ob_type->tp_iter != &_PyObject_NextNotImplemented)