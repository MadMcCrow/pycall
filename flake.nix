# simple flake to provide picall to whomever needs it
{
  inputs = {
    nixpkgs.url = github:NixOS/nixpkgs;
  };
  outputs =
    { nixpkgs, ... }@inputs:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "aarch64-darwin"
        "aarch64-linux"
      ];
      # define system flake
      flake = system :
        let 
          pkgs = nixpkgs.legacyPackages.${system};
        in {
        legacyPackages.${system}    = builtins.listToAttrs 
        # for each version provide a package
        ( map (x : { name = x.name ; value = { pycall = pkgs.callPackage ./nix/package.nix {python = x;};};})
        # supported python versions :
        [ pkgs.python310 pkgs.python311 pkgs.python312] );
        
        # default shell, uses 
        devShells.${system}.default = pkgs.callPackage ./nix/shell.nix  {python = pkgs.python311;};

        # TODO :
        # apps.${system} = pkgs.callPackages ./nix/apps.nix args;
      }; 
    in
    # for each supported system
    builtins.foldl' (x: y:  nixpkgs.lib.recursiveUpdate x y) { } (map flake systems);
    
}
