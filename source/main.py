import os
import sys
import argparse
import requests
import tarfile
import shutil

def download_latest_libnx():
    """Downloads the latest libnx source tarball from GitHub."""
    print("Finding latest libnx release...")
    api_url = "https://api.github.com/repos/switchbrew/libnx/releases/latest"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        release_data = response.json()

        asset_url = release_data.get('tarball_url')

        if not asset_url:
            print("Could not find a suitable asset to download.")
            return None

        print(f"Downloading from {asset_url}")
        response = requests.get(asset_url, stream=True)
        response.raise_for_status()

        tag_name = release_data.get('tag_name', 'latest')
        filename = f"libnx-{tag_name}.tar.gz"
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Downloaded {filename}")
        return filename
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while downloading: {e}")
        return None

def print_recompilation_instructions():
    """Prints recompilation instructions to the user."""
    print("\nTo recompile your project with the updated libnx, run the following commands:")
    print("  make clean")
    print("  make")

def replace_libnx(project_path, libnx_archive_path, args):
    """Replaces the libnx/nx directory in the project path with the new one."""
    print(f"Extracting {libnx_archive_path}...")
    toplevel_dir = None
    try:
        with tarfile.open(libnx_archive_path, "r:gz") as tar:
            tar.extractall()
            toplevel_dir = tar.getnames()[0].split(os.path.sep)[0]

        source_nx_path = os.path.join(toplevel_dir, 'nx')
        if not os.path.isdir(source_nx_path):
            print("Could not find an 'nx' directory in the extracted archive.")
            return

        target_path_libnx = os.path.join(project_path, 'libnx')
        target_path_nx = os.path.join(project_path, 'nx')
        target_path = None

        if os.path.isdir(target_path_libnx):
            target_path = target_path_libnx
        elif os.path.isdir(target_path_nx):
            target_path = target_path_nx
        
        if not target_path:
            print("No local 'libnx' or 'nx' directory found in the project.")
            print("This tool only patches projects with a local copy of the library.")
            print("If your project uses libnx from devkitPro, please update it by running:")
            print("  dkp-pacman -Syu switch-dev")
            return

        print(f"Found existing library at: {target_path}")
        print("This will be DELETED and replaced with the latest version.")
        
        if not args.yes:
            confirm = input("Are you sure you want to continue? (y/N): ")
            if confirm.lower() != 'y':
                print("Aborting. No changes have been made.")
                return

        print(f"Replacing {target_path}...")
        shutil.rmtree(target_path)
        shutil.move(source_nx_path, target_path)
        print("Successfully replaced libnx.")
        print_recompilation_instructions()

    except (tarfile.TarError, OSError, IndexError) as e:
        print(f"An error occurred during the replacement process: {e}")
    finally:
        if toplevel_dir and os.path.exists(toplevel_dir):
            shutil.rmtree(toplevel_dir)

def main():
    parser = argparse.ArgumentParser(description="Libnx Source Patcher")
    parser.add_argument("project_path", help="Path to the homebrew project")
    parser.add_argument("-y", "--yes", action="store_true", help="Automatically answer yes to prompts")
    args = parser.parse_args()

    if not os.path.isdir(args.project_path):
        print(f"Error: The specified path '{args.project_path}' is not a valid directory.")
        sys.exit(1)
    
    print(f"Project path: {args.project_path}")
    libnx_archive = download_latest_libnx()
    if libnx_archive:
        replace_libnx(args.project_path, libnx_archive, args)
        if os.path.exists(libnx_archive):
            os.remove(libnx_archive)

if __name__ == "__main__":
    main()
