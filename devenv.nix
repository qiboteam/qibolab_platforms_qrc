{
  config,
  pkgs,
  ...
}:
{
  packages = with pkgs; [
    poethepoet
    pre-commit
    stdenv.cc.cc.lib
  ];

  env = {
    QIBOLAB_PLATFORMS = config.env.DEVENV_ROOT;
    LD_LIBRARY_PATH = builtins.concatStringsSep ":" (
      map (p: "${p}/lib") (
        with pkgs;
        [
          stdenv.cc.cc.lib
          zlib
        ]
      )
    );
  };

  languages.python = {
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
}
