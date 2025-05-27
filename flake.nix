{
  description = "Nix flake for the prefect-flow-iiif-manifest-etl";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSupportedSystem = f: nixpkgs.lib.genAttrs supportedSystems (system: f {
        pkgs = import nixpkgs { inherit system; };
      });
    in
    {
      devShells = forEachSupportedSystem ({ pkgs }: {
        default = pkgs.mkShell {
          LD_LIBRARY_PATH = "${pkgs.stdenv.cc.cc.lib}/lib";
          venvDir = ".venv";
          packages = with pkgs; [ 
            pyright
            python312 
            uv
          ] ++
            (with pkgs.python312Packages; [
              venvShellHook
              ruff
            ]);
        };
      });
    };
}
