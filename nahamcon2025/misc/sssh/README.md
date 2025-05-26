# SSSH

Author: @JohnHammond

Haven't you always wanted a Super Secure Shell key manager!?! Now you've got it, with our super secure Super Secure Shell utility, SSSH!

It's so secure, you can even run it with privileges!

The flag is in the root user's home directory.

Connect to this challenge with ssh and the approprite port number. Username is user and password is userpass.

On sshing into the challenge:

```sh
└─$ ssh -p 30641 user@challenge.nahamcon.com
The authenticity of host '[challenge.nahamcon.com]:30641 ([104.198.232.26]:30641)' can't be established.
ED25519 key fingerprint is SHA256:O/asLJnkuZd7A7hIwUfhJlA29Li1ZdmB/kqqHOpfH3E.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '[challenge.nahamcon.com]:30641' (ED25519) to the list of known hosts.
user@challenge.nahamcon.com's password: 

The SSSH utility is located in the /opt directory.
user@sssh:~$ ls
```


```sh
user@sssh:/opt$ ll
total 20
drwxr-xr-x    1 root     root          4096 May 23 18:06 ./
drwxr-xr-x    1 root     root          4096 May 24 07:01 ../
-r-xr-xr-x    1 root     root         10206 May 23 18:05 sssh.sh*
```

```sh
user@sssh:/opt$ cat sssh.sh
#!/bin/bash

# SSSH - Super Secure Shell Key Manager

HEADER_WIDTH=76
HEADER_MARGIN="1 2"
HEADER_PADDING="2 4"
HEADER_FG=212
HEADER_BORDER_FG=212

BOX_WIDTH=50
BOX_MARGIN="2 2"
BOX_PADDING="1 2"
BOX_FG=212
BOX_BORDER_FG=212

ERROR_FG=196
ERROR_BORDER_FG=196
SUCCESS_FG=46
SUCCESS_BORDER_FG=46

if ! command -v gum &> /dev/null; then
    echo "Error: gum is not installed. Please install it first:"
    echo "go install github.com/charmbracelet/gum@latest"
    exit 1
fi

if [ ! -d ~/.ssh ]; then
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh
fi


gum style \
    --foreground "$HEADER_FG" --border-foreground "$HEADER_BORDER_FG" --border double \
    --align center --width "$HEADER_WIDTH" --margin "$HEADER_MARGIN" --padding "$HEADER_PADDING" \
    'SSSH - Super Secure Shell Key Manager' 'Your keys are safe with us!'

list_keys() {
    files=$(find ~/.ssh -type f 2>/dev/null)
    
    if [ -z "$files" ]; then
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "No files found in ~/.ssh"
        return 1
    fi

    key_list=""
    for file in $files; do
        key_list+="$file\n"
    done

    selected_file=$(echo -e "$key_list" | gum filter --header "Select a file to view from ~/.ssh" --placeholder "Search files...")
    
    selected_file=$(echo "$selected_file" | cut -d' ' -f1)
    
    if [ -n "$selected_file" ]; then
        if [ ! -r "$selected_file" ]; then
            gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Permission denied: Cannot read $selected_file"
            return 1
        fi

        gum pager < "$selected_file"
    fi
}

is_valid_input() {    
    if [[ "$1" =~ [\;\&\|\>\<\`\[\]\(\)\$\'\"\\\/] ]]; then
        return 1
    fi
    return 0
}

is_valid_destination() {
    if [[ "$1" == *".."* ]] || [[ "$1" == *"/"* ]]; then
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Unsafe destination"
        return 1
    fi
    if ! is_valid_input "$1"; then
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Invalid destination: Dangerous characters"
        return 1
    fi
    return 0
}


generate_key() {
    key_type=$(gum choose --header "Select Key Type for ~/.ssh" "RSA" "Ed25519" "ECDSA")
    
    case "$key_type" in
        "RSA")
            default_name="id_rsa"
            ;;
        "Ed25519")
            default_name="id_ed25519"
            ;;
        "ECDSA")
            default_name="id_ecdsa"
            ;;
    esac

    if ! is_valid_input "$default_name"; then
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Invalid default key name: Dangerous characters"
        return 1
    fi

    key_name=$(gum input --value "$default_name" --placeholder "Enter custom key name (will be saved in ~/.ssh/)" --prompt "Key Name: ")
    key_name=$(basename "$key_name")

    if ! is_valid_input "$key_name"; then
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Invalid input filename: Dangerous characters"
        return 1
    fi
    
    passphrase=$(gum input --password --placeholder "Enter passphrase (optional)" --prompt "Passphrase: ")
    
    if ! is_valid_input "$passphrase"; then
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Invalid passphrase: Dangerous characters"
        return 1
    fi
    
    comment=$(gum input --placeholder "Enter comment for key (optional)" --prompt "Comment: ")
    
    if ! is_valid_input "$comment"; then
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Invalid comment: Dangerous characters"
        return 1
    fi
    
    if [ -f ~/.ssh/"$key_name" ] || [ -f ~/.ssh/"$key_name.pub" ]; then
        if ! gum confirm "Key ~/.ssh/$key_name already exists. Overwrite?"; then
            return
        fi
        overwrite_flag="-y"
    else
        overwrite_flag=""
    fi
    
    mkdir -p ~/.ssh
    chmod 700 ~/.ssh

    if [ -n "$comment" ]; then
        error_output=$(gum spin --spinner dot --title "Generating key in ~/.ssh..." -- \
            ssh-keygen $overwrite_flag -C $comment -t $key_type -f ~/.ssh/"$key_name" -N "$passphrase" 2>&1)
    else
        error_output=$(gum spin --spinner dot --title "Generating key in ~/.ssh..." -- \
            ssh-keygen $overwrite_flag -t $key_type -f ~/.ssh/"$key_name" -N "$passphrase" 2>&1)
    fi
    
    if [ $? -eq 0 ]; then
        chmod 600 ~/.ssh/"$key_name"
        chmod 644 ~/.ssh/"$key_name.pub"
        gum style --foreground "$SUCCESS_FG" --border-foreground "$SUCCESS_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Key generated successfully in ~/.ssh/$key_name"
    else
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Failed to generate key in ~/.ssh/$key_name: $error_output"
    fi
}

import_key() {
    key_file=$(gum file --file --header "Select a key file to import into ~/.ssh")
    
    if [ -z "$key_file" ]; then
        return 1
    fi

    if ! is_valid_input "$key_file"; then
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Invalid source file path: Dangerous characters"
        return 1
    fi

    if [ ! -r "$key_file" ]; then
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Permission denied: Cannot read source file $key_file"
        return 1
    fi

    dest_name=$(gum input --placeholder "Enter destination name (will be saved in ~/.ssh/)" --prompt "Destination Name: ")
    dest_name=$(basename $dest_name)

    if ! is_valid_destination "$dest_name"; then
        return 1
    fi
    
    if [ ! -w ~/.ssh ]; then
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Permission denied: Cannot write to ~/.ssh directory"
        return 1
    fi
    
    if gum confirm "Import key with these settings?"; then
        gum spin --spinner dot --title "Importing key to ~/.ssh/$dest_name..." -- \
            cp "$key_file" ~/.ssh/"$dest_name" && \
            chmod 600 ~/.ssh/"$dest_name"
        
        if [ $? -eq 0 ]; then
            gum style --foreground "$SUCCESS_FG" --border-foreground "$SUCCESS_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Key imported successfully to ~/.ssh/$dest_name"
        else
            gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Failed to import key to ~/.ssh/$dest_name"
        fi
    fi
}

delete_key() {
    files=$(find ~/.ssh -type f 2>/dev/null)
    
    if [ -z "$files" ]; then
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "No files found in ~/.ssh"
        return 1
    fi

    file_to_delete=$(echo "$files" | gum filter --header "Select a file to delete from ~/.ssh" --placeholder "Search files...")
    
    if [ -z "$file_to_delete" ]; then
        return 1
    fi

    if [ ! -w "$file_to_delete" ]; then
        gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Permission denied: Cannot delete $file_to_delete"
        return 1
    fi
    
    if gum confirm "Are you sure you want to delete key $file_to_delete ?"; then
        gum spin --spinner dot --title "Deleting $file_to_delete..." -- \
            rm "$file_to_delete"
        if [ $? -eq 0 ]; then
            gum style --foreground "$SUCCESS_FG" --border-foreground "$SUCCESS_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "File deleted successfully: $file_to_delete"
        else
            gum style --foreground "$ERROR_FG" --border-foreground "$ERROR_BORDER_FG" --border double --align center --width "$BOX_WIDTH" --margin "$BOX_MARGIN" --padding "$BOX_PADDING" "Failed to delete file: $file_to_delete"
        fi
    fi
}

while true; do
    choice=$(gum choose --header "SSSH: Select an Option" "List Keys" "Generate New Key" "Import Key" "Delete Key" "Exit")
    
    case "$choice" in
        "List Keys")
            list_keys
            ;;
        "Generate New Key")
            generate_key
            ;;
        "Import Key")
            import_key
            ;;
        "Delete Key")
            delete_key
            ;;
        "Exit")
            gum style \
                --foreground "$HEADER_FG" --border-foreground "$HEADER_BORDER_FG" --border double \
                --align center --width "$HEADER_WIDTH" --margin "$HEADER_MARGIN" --padding "$HEADER_PADDING" \
                'Thank you for using SSSH!' 'Your keys are safe with us!'
            exit 0
            ;;
    esac
done
```
