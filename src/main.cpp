// =============================================================================
// Experiment: Sum of Subsets using Backtracking
// Subject   : Algorithm Design and Analysis (ADA)
// Language  : C++
// =============================================================================

#include <iostream>
#include <fstream>
#include <vector>
#include <algorithm>
#include <string>
#include <sstream>
#include <iomanip>

using namespace std;

// ---------------------------------------------------------------------------
// Global log buffer
// ---------------------------------------------------------------------------
vector<string> logLines;

void logMsg(const string& msg = "") {
    cout << msg << "\n";
    logLines.push_back(msg);
}

// ---------------------------------------------------------------------------
// Helper: format a vector as [a, b, c]
// ---------------------------------------------------------------------------
string vecToStr(const vector<int>& v) {
    string s = "[";
    for (int i = 0; i < (int)v.size(); i++) {
        s += to_string(v[i]);
        if (i + 1 < (int)v.size()) s += ", ";
    }
    s += "]";
    return s;
}

// ---------------------------------------------------------------------------
// Global solutions container
// ---------------------------------------------------------------------------
vector<vector<int>> solutions;
long long traceCallId = 0;

string indent(int depth) {
    return string(depth * 2, ' ');
}

// ---------------------------------------------------------------------------
// Core Backtracking Function
// ---------------------------------------------------------------------------
void sumOfSubsets(vector<int>& arr, int index,
                  vector<int>& currentSubset,
                  int currentSum, int target, int remaining,
                  int depth) {
    long long myCall = ++traceCallId;
    {
        ostringstream oss;
        oss << "  " << indent(depth)
            << "CALL #" << myCall
            << "  (index=" << index
            << ", sum=" << currentSum
            << ", remaining=" << remaining
            << ", subset=" << vecToStr(currentSubset) << ")";
        logMsg(oss.str());
        logMsg();
    }

    // --- Base Case: Target reached ---
    if (currentSum == target) {
        solutions.push_back(currentSubset);
        logMsg("  " + indent(depth) + "=> SOLUTION FOUND " + vecToStr(currentSubset) +
               "  (sum=" + to_string(currentSum) + ")");
        logMsg("  " + indent(depth) + "RETURN #" + to_string(myCall));
        logMsg();
        return;
    }

    int n = (int)arr.size();

    for (int i = index; i < n; i++) {
        {
            ostringstream oss;
            oss << "  " << indent(depth)
                << "TRY arr[" << i << "]=" << arr[i];
            logMsg(oss.str());
        }

        // --- Pruning: over-sum ---
        if (currentSum + arr[i] > target) {
            ostringstream oss;
            oss << "  " << indent(depth)
                << "PRUNE (over target) : " << currentSum
                << " + " << arr[i]
                << " = " << (currentSum + arr[i])
                << " > " << target;
            logMsg(oss.str());
            logMsg();
            break;  // sorted array: no point checking further
        }

        // --- Pruning: under-sum ---
        if (currentSum + remaining < target) {
            ostringstream oss;
            oss << "  " << indent(depth)
                << "PRUNE (insufficient possible sum) : "
                << currentSum << " + " << remaining
                << " = " << (currentSum + remaining)
                << " < " << target;
            logMsg(oss.str());
            logMsg();
            break;
        }

        // --- Include arr[i] ---
        currentSubset.push_back(arr[i]);
        {
            ostringstream oss;
            oss << "  " << indent(depth)
                << "CHOOSE arr[" << i << "]=" << setw(3) << arr[i]
                << "  -> sum " << currentSum
                << " + " << arr[i]
                << " = " << setw(4) << (currentSum + arr[i])
                << "  subset=" << vecToStr(currentSubset);
            logMsg(oss.str());
        }

        // Recurse
        sumOfSubsets(arr, i + 1, currentSubset,
                     currentSum + arr[i], target, remaining - arr[i], depth + 1);

        // --- Exclude arr[i] (Backtrack) ---
        currentSubset.pop_back();
        remaining -= arr[i];
        {
            ostringstream oss;
            oss << "  " << indent(depth)
                << "BACKTRACK remove arr[" << i << "]=" << setw(3) << arr[i]
                << "  subset=" << vecToStr(currentSubset);
            logMsg(oss.str());
            logMsg();
        }
    }
    logMsg("  " + indent(depth) + "RETURN #" + to_string(myCall));
    logMsg();
}

// ---------------------------------------------------------------------------
// Run one test case
// ---------------------------------------------------------------------------
void runExperiment(int testNum, vector<int> rawSet, int target) {
    solutions.clear();

    sort(rawSet.begin(), rawSet.end());
    int total = 0;
    for (int x : rawSet) total += x;

    string sep(70, '=');

    logMsg();
    logMsg(sep);
    logMsg("  TEST CASE " + to_string(testNum));
    logMsg(sep);
    logMsg("  Input Set    : " + vecToStr(rawSet));
    logMsg("  Sorted Set   : " + vecToStr(rawSet));   // already sorted
    logMsg("  Target Sum   : " + to_string(target));
    logMsg("  Total Sum    : " + to_string(total));
    logMsg(sep);

    if (target > total) {
        logMsg("  [INFO] Target " + to_string(target) +
               " exceeds total sum " + to_string(total) +
               ". No solution possible.");
        logMsg(sep);
        return;
    }

    logMsg("  Backtracking Trace:");
    logMsg();

    vector<int> subset;
    traceCallId = 0;
    sumOfSubsets(rawSet, 0, subset, 0, target, total, 0);

    logMsg();
    logMsg(sep);
    if (!solutions.empty()) {
        logMsg("  Total Solutions : " + to_string(solutions.size()));
        for (int i = 0; i < (int)solutions.size(); i++) {
            int s = 0;
            for (int x : solutions[i]) s += x;
            logMsg("    Solution " + to_string(i + 1) +
                   "    : " + vecToStr(solutions[i]) +
                   "  -->  Sum = " + to_string(s));
        }
    } else {
        logMsg("  No subset found that sums to the target.");
    }
    logMsg(sep);
    logMsg();
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
int main() {
    string sep(70, '=');

    logMsg(sep);
    logMsg("  EXPERIMENT: SUM OF SUBSETS USING BACKTRACKING");
    logMsg("  Subject     : Algorithm Design and Analysis (ADA)");
    logMsg("  Language    : C++");
    logMsg(sep);

    int n;
    logMsg("  Enter number of elements:");
    cout << "  > ";
    cin >> n;

    if (!cin || n <= 0) {
        cerr << "[ERROR] Invalid number of elements.\n";
        return 1;
    }

    vector<int> userSet(n);
    logMsg("  Enter elements (space-separated):");
    cout << "  > ";
    for (int i = 0; i < n; i++) {
        cin >> userSet[i];
        if (!cin) {
            cerr << "[ERROR] Invalid element input.\n";
            return 1;
        }
    }

    int target;
    logMsg("  Enter target sum:");
    cout << "  > ";
    cin >> target;
    if (!cin) {
        cerr << "[ERROR] Invalid target input.\n";
        return 1;
    }

    runExperiment(1, userSet, target);

    logMsg(sep);
    logMsg("  END OF EXPERIMENT");
    logMsg(sep);

    // -----------------------------------------------------------------------
    // Write output files
    // -----------------------------------------------------------------------
    string outputDir = "/Users/amiteshwarsingh/Documents/ADA/sos/output/";

    auto writeFile = [&](const string& path) {
        ofstream f(path);
        if (!f) { cerr << "[ERROR] Cannot open: " << path << "\n"; return; }
        for (const auto& line : logLines) f << line << "\n";
        cout << "[INFO] Output saved to: " << path << "\n";
    };

    writeFile(outputDir + "terminal_output.txt");
    writeFile(outputDir + "output.txt");

    return 0;
}
