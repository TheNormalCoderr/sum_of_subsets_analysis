#include <algorithm>
#include <fstream>
#include <iostream>
#include <vector>

using namespace std;

// Backtracking for subset sum: include/exclude each element.
void findSubsets(const vector<int>& arr,
                 int idx,
                 int target,
                 int currentSum,
                 vector<int>& current,
                 vector<vector<int>>& solutions) {
    if (currentSum == target) {
        solutions.push_back(current);
        return;
    }

    if (idx >= (int)arr.size() || currentSum > target) {
        return;
    }

    // Choice 1: include arr[idx]
    current.push_back(arr[idx]);
    findSubsets(arr, idx + 1, target, currentSum + arr[idx], current, solutions);
    current.pop_back();

    // Choice 2: exclude arr[idx]
    findSubsets(arr, idx + 1, target, currentSum, current, solutions);
}

string subsetToString(const vector<int>& subset) {
    string s = "[";
    for (int i = 0; i < (int)subset.size(); i++) {
        s += to_string(subset[i]);
        if (i + 1 < (int)subset.size()) s += ", ";
    }
    s += "]";
    return s;
}

int main() {
    int n;
    // Read number of elements in the set.
    cout << "Enter number of elements: ";
    cin >> n;

    // Basic input guard.
    if (!cin || n <= 0) {
        cerr << "Invalid number of elements.\n";
        return 1;
    }

    vector<int> arr(n);
    cout << "Enter elements: ";
    for (int i = 0; i < n; i++) cin >> arr[i];

    int target;
    cout << "Enter target sum: ";
    cin >> target;

    if (!cin) {
        cerr << "Invalid target.\n";
        return 1;
    }

    // Sorting keeps output tidy and predictable.
    sort(arr.begin(), arr.end());

    // Run backtracking search.
    vector<int> current;
    vector<vector<int>> solutions;
    findSubsets(arr, 0, target, 0, current, solutions);

    // Save summary and solutions to output file.
    const string outDir = "/Users/amiteshwarsingh/Documents/ADA/sos/output/";
    system(("mkdir -p " + outDir).c_str());
    ofstream out(outDir + "output.txt");
    if (!out) {
        cerr << "Cannot open output file.\n";
        return 1;
    }

    cout << "Total solutions: " << solutions.size() << "\n";
    out << "Array: ";
    for (int x : arr) out << x << " ";
    out << "\nTarget: " << target << "\n\n";

    if (solutions.empty()) {
        out << "No subset found.\n";
    } else {
        for (int i = 0; i < (int)solutions.size(); i++) {
            out << "Solution " << (i + 1) << ": " << subsetToString(solutions[i]) << "\n";
        }
    }

    cout << "Output saved to: " << outDir << "output.txt\n";
    return 0;
}
