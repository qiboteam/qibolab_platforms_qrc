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
      systems = ["x86_64-linux" "aarch64-darwin"];

      perSystem = {
        pkgs,
        config,
        ...
      }: {
        devenv.shells.default = {
          packages = with pkgs; [poethepoet pre-commit stdenv.cc.cc.lib];

          env = {
            LD_LIBRARY_PATH = builtins.concatStringsSep ":" (map (p: "${p}/lib") (with pkgs; [
              stdenv.cc.cc.lib
              zlib
            ]));
          };

          languages = {
            python = {
              enable = true;
              venv = {
                enable = true;
                requirements = ''
                  qibolab [qblox] @ git+https://github.com/qiboteam/qibolab.git@qblox

                  # dev deps
                  ipython
                  pdbpp
                '';
              };
            };
          };
        };
      };
    };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };
}
