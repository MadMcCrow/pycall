{
  pkgs ? import <nixpkgs> { },
  lib,
  python ? pkgs.python311,
  ...
}:
with pkgs;
let 
nixtools = [ nixfmt-rfc-style deadnix ];

in 
mkShell {
  packages = [  
    python
  ] ++ (with python.pkgs; [
    ccache
    poetry-core
  ]);
}
