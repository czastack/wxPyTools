#pragma once

namespace pybind11 {
	class module;
}

void init_emuhacker(pybind11::module &m);