#include <iostream>
#include <numeric>
#include <vector>

int main() {
    const std::vector<int> values{1, 2, 3, 4};
    if (std::accumulate(values.begin(), values.end(), 0) != 10) {
        return 1;
    }
    std::cout << "Emscripten C++ runtime test passed\n";
    return 0;
}
