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

def replace_libnx(project_path, archive_path, args):
    """Replaces the libnx folder in the project with the one from the archive."""
    toplevel_dir = None
    try:
        print("Extracting archive...")
        with tarfile.open(archive_path, "r:gz") as tar:
            members = tar.getmembers()
            if not members:
                print("Error: The archive is empty.")
                return
            
            toplevel_dir = members[0].name.split('/')[0]
            tar.extractall()

        # Path to the actual library source inside the extracted GitHub tarball
        source_nx_path = os.path.join(toplevel_dir, "nx")
        
        if not os.path.exists(source_nx_path):
            print(f"Error: Could not find 'nx' directory inside the extracted archive at {source_nx_path}.")
            return

        # Common directory names used in homebrew projects for libnx source
        potential_paths = [
            os.path.join(project_path, "libnx"),
            os.path.join(project_path, "nx")
        ]
        
        target_path = None
        for path in potential_paths:
            if os.path.exists(path):
                target_path = path
                break
        
        if not target_path:
            # If neither exists, we default to creating 'libnx' in the project root
            target_path = os.path.join(project_path, "libnx")
            print(f"Note: No existing libnx folder found. Will create new one at {target_path}")
        else:
            print(f"Warning: {target_path} will be DELETED and replaced with the latest version.")

        if not args.yes:
            confirm = input("Are you sure you want to continue? (y/N): ")
            if confirm.lower() != 'y':
                print("Aborting. No changes have been made.")
                return

        print(f"Updating {target_path}...")
        
        # Remove old folder if it exists
        if os.path.exists(target_path):
            if os.path.isfile(target_path):
                os.remove(target_path)
            else:
                shutil.rmtree(target_path)
        
        # Move the new source into place
        shutil.move(source_nx_path, target_path)
        
        print("Successfully patched libnx source.")
        print_recompilation_instructions()

    except (tarfile.TarError, OSError, IndexError) as e:
        print(f"An error occurred during the replacement process: {e}")
    finally:
        # Cleanup
        if toplevel_dir and os.path.exists(toplevel_dir):
            shutil.rmtree(toplevel_dir)
        if os.path.exists(archive_path):
            os.remove(archive_path)

def main():
    parser = argparse.ArgumentParser(description="Libnx Source Patcher")
    parser.add_argument("project_path", help="Path to the homebrew project source code")
    parser.add_argument("-y", "--yes", action="store_true", help="Automatically answer yes to prompts")
    args = parser.parse_args()

    # Expand user paths (like ~/) if provided
    args.project_path = os.path.expanduser(args.project_path)

    if not os.path.isdir(args.project_path):
        print(f"Error: The specified path '{args.project_path}' is not a valid directory.")
        sys.exit(1)
    
    print(f"Project path: {args.project_path}")
    libnx_archive = download_latest_libnx()
    if libnx_archive:
        replace_libnx(args.project_path, libnx_archive, args)
    else:
        print("Failed to download libnx. Check your connection to GitHub.")

if __name__ == "__main__":
    main()
