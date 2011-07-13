#include <iostream>

#include "num_util.h"
#include "trajectory.h"
#include "DCDLoader.h"

using namespace std;
using namespace boost::python;
namespace bnp=boost::python::numeric;

void hello()
    {
    cout << "hello." << endl;
    }

void test(bnp::array inValue)
    {
    num_util::check_type(inValue, PyArray_FLOAT);
    num_util::check_rank(inValue, 1);
    float* dataPtr = (float*) num_util::data(inValue);
    int theSize= num_util::size(inValue);
    std::cout << std::endl << "data values on c++ side: " << std::endl;
    for(int i=0;i < theSize;++i)
        {
        std::cout << *(dataPtr + i) << std::endl;
        }
    }
 
void export_trajectory()
    {
    // define functions
    def("hello", &hello);
    def("test", &test);
    class_<Box>("Box", init<float, optional<bool> >())
        .def(init<float, float, float, optional<bool> >())
        .def("set2D", &Box::set2D)
        .def("is2D", &Box::is2D)
        .def("getLx", &Box::getLx)
        .def("getLy", &Box::getLy)
        .def("getLz", &Box::getLz)
        .def("getVolume", &Box::getVolume)
        .def("wrap", &Box::wrapPy)
        /*.def("unwrap", &Box::unwrapPy)
        .def("makeunit", &Box::makeunitPy)*/
        ;
    export_dcdloader();
    }

