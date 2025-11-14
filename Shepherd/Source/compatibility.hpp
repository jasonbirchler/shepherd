/*
  ==============================================================================
  
    compatibility.hpp
    Created: Compatibility fixes for third-party library issues
  
  ==============================================================================
*/

#pragma once

// Include missing C++ standard library headers that some JUCE components need
#include <utility>  // For std::exchange

// If needed, provide a fallback std::exchange implementation for older compilers
#if __cplusplus < 201402L && !defined(__cpp_lib_exchange)
namespace std {
    template<typename T, typename U>
    constexpr T exchange(T& obj, U&& new_value) {
        T old_value = std::move(obj);
        obj = std::forward<U>(new_value);
        return old_value;
    }
}
#endif
