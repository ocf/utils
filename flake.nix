{
  description = "User and staff utilities for the OCF";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    ocflib.url = "github:ocf/ocflib";
  };

  outputs = { self, nixpkgs, flake-utils, ocflib }: flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [ ocflib.overlays.default ];
      };
      package = pkgs.callPackage ./default.nix { };
    in
    {
      packages.default = package;
      packages.ocf-utils = package;
    }
  );
}
