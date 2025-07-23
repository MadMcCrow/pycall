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
      pythons = [
        "python310"
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
              packageOverrides = final: prev: {
                pycall = final.callPackage ./nix/package.nix { inherit python; };
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
