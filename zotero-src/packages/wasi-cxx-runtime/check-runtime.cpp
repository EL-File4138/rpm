#include <algorithm>
#include <string>
#include <vector>

int main() {
    std::vector<std::string> values = {"zotero", "source", "build"};
    std::sort(values.begin(), values.end());
    return values.front() == "build" && values.back() == "zotero" ? 0 : 1;
}
