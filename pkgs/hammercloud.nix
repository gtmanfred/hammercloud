let
  pkgs = import <nixpkgs> {};
  pname = "hammercloud";
in

{ stdenv ? pkgs.stdenv
, pythonPackages ? pkgs.python3Packages
, git ? pkgs.gitMinimal
}:

with pythonPackages;
let hammercloud = 
  buildPythonPackage rec {
    name = pname;
    src = ../.;
    buildInputs = [git pbr];
    # These are dependencies that will need to be called by the application
    # when it runs
    propagatedBuildInputs = [ python requests pexpect ];
  };
in stdenv.mkDerivation {
  name = pname;
  buildInputs = [ hammercloud ];
}
