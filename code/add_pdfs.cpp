/*
 * Toy simulation of finding an efficiency using Monte-Carlo
 */
#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <fstream>
#include <functional>
#include <iostream>
#include <iterator>
#include <random>
#include <vector>

namespace
{

/*
 * Gaussian PDF
 */
inline double gaussPDF(const double x, const double m, const double s)
{
    static constexpr float inv_sqrt_2pi = 0.3989422804014327;
    float                  a            = (x - m) / s;

    return inv_sqrt_2pi / s * std::exp(-0.5f * a * a);
}

/*
 * Generate nGen events, throw some away with accept-reject sampling to make the distribution look like
 * the PDF we want
 *
 */
std::vector<double> sample(std::mt19937&                        gen,
                           const size_t                         nGen,
                           const std::function<double(double)>& pdf,
                           const std::pair<double, double>&     range,
                           const std::pair<double, double>&     domain)
{
    std::uniform_real_distribution<double> domainDis(domain.first, domain.second);
    std::uniform_real_distribution<double> rangeDis(range.first, range.second);

    std::vector<double> rv{};
    for (size_t i = 0; i < nGen; ++i) {
        double x = domainDis(gen);
        double y = rangeDis(gen);
        if (y < pdf(x)) {
            rv.push_back(x);
        }
    }

    return rv;
}

/*
 * Linspace
 */
std::vector<double> linspace(const std::pair<double, double>& domain)
{
    std::vector<double> rv;

    constexpr size_t n{100};
    double           delta = (domain.second - domain.first) / (n - 1);

    for (size_t i = 0; i < n - 1; ++i) {
        rv.push_back(domain.first + delta * i);
    }
    rv.push_back(domain.second);
    return rv;
}

/*
 * Integral by splitting the domain into trapezia
 */
/*
 * Save a vector to a csv file
 */
void vector2csv(const std::vector<double>& v, const std::string& path)
{
    std::ofstream handle(path);

    // Write all the values except the last with a comma in between
    for (size_t i = 0; i < v.size() - 1; ++i)
        handle << v[i] << ',';

    // Write the last value without a trailing comma
    handle << v[v.size() - 1];
}

/*
 * Dump a load of x and function values to a csv file
 */
void dumpVals(const std::string&                   path,
              const std::pair<double, double>&     domain,
              const std::function<double(double)>& fcn)
{
    // Find values on the domain
    auto x = linspace(domain);

    // Evaluate function here
    std::vector<double> y = x;
    std::transform(x.begin(), x.end(), y.begin(), fcn);

    vector2csv(x, "domain_" + path);
    vector2csv(y, "vals_" + path);
}

/*
 * Find the c-factor given a reconstructed sample and its PDF

 */
double factor(const std::vector<double>& v, const std::function<double(double)>& f)
{
    double i{0.0};

    for (const auto x : v) {
        i += 1 / f(x);
    }

    return i;
}

} // namespace

int main(int argc, char* argv[])
{
    // Either provide 0 or 2 CLI args
    assert((argc == 1 || argc == 3) && "pass exactly 2 CLI args (evt numbers)");

    const size_t n1 = (argc == 3) ? std::atoi(argv[1]) : 10000;
    const size_t n2 = (argc == 3) ? std::atoi(argv[2]) : 10000;

    // Setup stuff for RNGs
    std::random_device rd{};
    auto               gen = std::mt19937(rd());

    const std::pair<double, double> domain{-2, 6};
    const std::pair<double, double> range{0, 1};

    // Define distributions and efficiency
    auto f          = [](double x) { return 7.0 * gaussPDF(x, 0.0, 3.0); };
    auto g          = [](double x) { return 9.0 * gaussPDF(x, 4.0, 4.0); };
    auto efficiency = [](double x) { return 0.2 + 4.6 * gaussPDF(x, 2.3, 3.0) * sin(x) * sin(x); };

    // Dump some values to file so I can plot them later with matplotlib
    dumpVals("f.csv", domain, f);
    dumpVals("g.csv", domain, g);
    dumpVals("efficiency.csv", domain, efficiency);

    // Generate points from both samples modulated by the efficiency
    const auto fSamples = sample(gen, n1, [&efficiency, &f](double x) { return f(x) * efficiency(x); }, range, domain);
    const auto gSamples = sample(gen, n2, [&efficiency, &g](double x) { return g(x) * efficiency(x); }, range, domain);

    vector2csv(fSamples, "fsamples.csv");
    vector2csv(gSamples, "gsamples.csv");

    // Find correction factors
    auto cF = factor(fSamples, f);
    auto cG = factor(gSamples, g);

    // Scale them
    // We have to be sure to scale such that the combined "PDF" doesn't
    // have a maximum density > 1, otherwise that will break my accept-reject code
    const auto scaleFactor = cF + cG;
    cF /= scaleFactor;
    cG /= scaleFactor;

    // Build an approximate generated PDF
    auto approx = [&f, &g, &cF, &cG](double x) { return cF * f(x) + cG * g(x); };
    dumpVals("approx.csv", domain, approx);

    // Generate some points from this generating PDF
    const auto approxSamples = sample(gen, n1 + n2, approx, range, domain);

    vector2csv(approxSamples, "approxsamples.csv");
}