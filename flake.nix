{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    devenv = {
      url = "github:cachix/devenv";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    flake-parts.url = "github:hercules-ci/flake-parts";
  };

  outputs = {
    self,
    nixpkgs,
    devenv,
    flake-parts,
    ...
  } @ inputs:
    flake-parts.lib.mkFlake {inherit inputs;} {
      imports = [inputs.devenv.flakeModule];
      systems = [
        "x86_64-linux"
        "aarch64-darwin"
      ];

      perSystem = {
        pkgs,
        config,
        ...
      }: {
        devenv.shells.default = {
          packages = with pkgs; [
            poethepoet
            pre-commit
            stdenv.cc.cc.lib
          ];

          env = {
            LD_LIBRARY_PATH = builtins.concatStringsSep ":" (
              map (p: "${p}/lib") (
                with pkgs; [
                  stdenv.cc.cc.lib
                  zlib
                ]
              )
            );
          };

          languages = {
            python = {
              enable = true;
              venv = {
                enable = true;
                requirements = ''
                  qibolab

                  # dev deps
                  ipython
                  # pudp
                '';
              };
            };
          };
        };
      };
    };
}
