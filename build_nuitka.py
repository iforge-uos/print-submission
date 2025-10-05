import sys
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import get_path
import hashbrowns



if __name__ == "__main__":
    # Normalize project name
    if len(sys.argv) < 2:
        print("Usage: python build.py <project_name> [output_filename]")
        sys.exit(1)

    project_name = sys.argv[1].lower().replace(" ", "_")

    # --- First hashbrown update (increment version) ---
    with hashbrowns.Hashbrown(password=project_name, build_mode=False) as hashbrown:
        data = hashbrown.decrypted_data
        version_string = datetime.now().strftime("%y%m%d")
        data["Version"] = int(version_string)
        hashbrown.encrypted_data = hashbrown.encrypt(data)
        hashbrown.write_encrypted()

    # --- Build mode ---
    with hashbrowns.Hashbrown(password=project_name, build_mode=True) as hashbrown:
        my_date = datetime.now()
        output_filename = (
            sys.argv[2]
            if len(sys.argv) > 2
            else f"Print Queue Program V.{my_date.strftime('%y%m%d')}"
        )

        script_dir = Path(__file__).parent.resolve()
        resources_dir = script_dir / "resources"
        secrets_dir = resources_dir / "secrets.json.enc"  # explicitly included
        main_script = str(script_dir / "main.py")

        # Safety checks
        if not resources_dir.exists():
            raise FileNotFoundError(f"Resources folder not found: {resources_dir}")
        if not secrets_dir.exists():
            print(f"Warning: secrets folder not found at {secrets_dir}")

        # Optional cleanup before build
        for folder in ("build", "dist"):
            path = script_dir / folder
            if path.exists():
                shutil.rmtree(path)

        # Build command
        cmd = [
            sys.executable,
            "-m",
            "nuitka",
            "--standalone",
            "--onefile",
            "--enable-plugin=pyqt5",
            "--windows-console-mode=disable",
            # Include full resources directory (including secrets)
            f"--include-data-dir={str(resources_dir)}={resources_dir.name}",
            # Windows icon
            f"--windows-icon-from-ico={str(resources_dir / 'printq50icon.ico')}",
            # Output filename
            f"--output-filename={output_filename}",
            # Entry point
            main_script,
        ]

        print("Running Nuitka build...")
        subprocess.run(cmd, check=True)

        paths_to_cleanup = [
            Path("build"),  # Nuitka build folder
            Path("__pycache__"),  # Python cache
            Path("main.build"),  # Sometimes generated build files
            Path("main.onefile-build"),  # Sometimes generated build files
            Path("main.dist")  # Sometimes generated build files
        ]

        for path in paths_to_cleanup:
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
        print("\nBuild finished successfully!")

        # Verification tip (optional)
        print("Checking resource path resolution:")
        print("  Example resource path:", get_path.nuitka("resources/secrets"))
