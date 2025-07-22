# build pycall with poetry
{pkgs,  python ? pkgs.python311, lib, ... }:
# simplify notation :
with builtins;
let
  # recursively find the intersection of list of list
  # this is used to be sure we support every platform that is supported by our inputs
  recintersect = l: lib.fold (xs: xss: intersectLists xss xs) (head l) (tail l);


in python.pkgs.buildPythonPackage rec {
    # version and name, 
    # TODO retrieve from pyproject file ! 
    pname = "pycall";
    version = "0.1.0";

    # sources are in the parent folder
    src = ../src;
    # poetry need this :
    pyproject = true;

    # necessary for build 
    buildInputs = [ python.pkgs.poetry-core ];
    propagatedBuildInputs = buildInputs;

    # meaningful meta 
    meta = {
      # TODO : complete
      licences = [ licences.mit ];
      # allow use on all compatible platforms
      platforms = recintersect (map (x: x.meta.platforms) buildInputs);
    };
}

