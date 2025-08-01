# simple flake to provide picall to whomever needs it
{
  inputs = {
    #nixpkgs.url = "github:NixOS/nixpkgs";
    nixpkgs = {
      type = "indirect";
      id = "nixpkgs";
    };
  };
  outputs =
    { nixpkgs, ... }@inputs:
    let
      # supported systems
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
        "aarch64-linux"
      ];
      # supported pythons :
      # asyncio runners are available starting with python 3.11
      pythons = [
        "python311"
        "python312"
      ];

      # define system flake
      flake =
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          # adding pycall to python packages :
          pythonOverride =
            python:
            python.override {
              packageOverrides = final: prev:
              with python.pkgs; {
                pycall = buildPythonPackage rec {
                  pname = "pycall";
                  version = "0.1.0"; # TODO retrieve from pyproject file !
                  src = ./src;
                  pyproject = true;
                  buildInputs = [ poetry-core rich ];
                  propagatedBuildInputs = buildInputs;
                  meta = with pkgs.lib; {
                    licences = [ licences.mit ];
                    platforms = platforms.x86_64 ++ platforms.aarch;
                  };
                };

              };
            };

        in
        {
          packages.${system} = builtins.listToAttrs (
            map (x: {
              name = x;
              value = pythonOverride (builtins.getAttr x pkgs);
            }) pythons
          );

          # default shell, uses
          devShells.${system}.default = pkgs.callPackage ./nix/shell.nix { python = pkgs.python311; };

          # TODO :
          # apps.${system} = pkgs.callPackages ./nix/apps.nix args;
        };
    in
    # for each supported system
    builtins.foldl' (x: y: nixpkgs.lib.recursiveUpdate x y) { } (map flake systems);

}
