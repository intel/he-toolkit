#pragma once

namespace hekit::coder {

// specialisations are kept in the appropriate scheme files
template <typename Scheme>
class Coder {
  // Specialisations only
  static_assert(!std::is_same<Scheme, Scheme>(),
                "Only allowed schemes can be used");
  // Pointless ctor is required for CTAD
  explicit Coder(const Scheme& params) {}
};

}  // namespace hekit::coder
