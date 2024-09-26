{ lib, python3Packages, bash, wakeonlan }:

python3Packages.buildPythonApplication {
  pname = "ocf-utils";
  version = "2024-04-22";
  format = "other";

  src = ./.;

  dontBuild = true;
  installPhase = ''
    mkdir -p $out/bin $out/sbin
    cp bin/* $out/bin
    cp sbin/* $out/sbin
  '';
  doCheck = false;

  buildInputs = [ bash wakeonlan ];

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
