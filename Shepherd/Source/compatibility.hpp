#pragma once

#include <utility>

// Compatibility shim for older compilers/standard libraries
#if !defined(__cpp_lib_exchange_function) || __cpp_lib_exchange_function < 201304L
namespace std {
    template<class T, class U = T>
    constexpr T exchange(T& obj, U&& new_value) {
        T old_value = std::move(obj);
        obj = std::forward<U>(new_value);
        return old_value;
    }
}
#endif