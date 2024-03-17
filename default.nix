{ lib, python3Packages, bash }:

python3Packages.buildPythonApplication {
  pname = "ocf-utils";
  version = "2024-03-17";
  format = "other";

  src = ./.;

  dontBuild = true;
  installPhase = "cp -r . $out";
  doCheck = false;

  buildInputs = [ bash ];

  propagatedBuildInputs = with python3Packages; [
    dnspython
    ocflib
    matplotlib
    tabulate
  ];

  meta = with lib; {
    description = "User and staff utilities for the OCF";
    homepage = "https://github.com/ocf/utils";
    license = [ licenses.asl20 licenses.gpl2Plus ];
    platforms = platforms.unix;
  };
}
