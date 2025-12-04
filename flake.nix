{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    devenv = {
      url = "github:cachix/devenv";
      inputs.nixpkgs.follows = "nixpkgs";
    };
    flake-parts.url = "github:hercules-ci/flake-parts";
    nixpkgs-python = {
      url = "github:cachix/nixpkgs-python";
      inputs = {nixpkgs.follows = "nixpkgs";};
    };
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

      perSystem = {pkgs, ...}: {
        devenv.shells.default = {config, ...}: {
          packages = with pkgs; [
            poethepoet
            pre-commit
            stdenv.cc.cc.lib
          ];

          env = {
            QIBOLAB_PLATFORMS = config.env.DEVENV_ROOT;
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
              version = "3.12";
              venv = {
                enable = true;
                requirements = ''
                  qibolab
                  qibolab-qblox
                  qibolab-qm

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
