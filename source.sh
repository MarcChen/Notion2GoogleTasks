source_all_envs_and_export() {
    project_root="$1"
    if [[ -z "$project_root" ]]; then
        echo "Usage: source_all_envs_and_export <project_root>"
        return 1
    fi

    # Find all .env files
    while IFS= read -r env_file; do
        echo "Processing environment file: $env_file"
        while IFS= read -r line || [[ -n "$line" ]]; do
            # Ignore comments and empty lines
            if [[ "$line" =~ ^[[:space:]]*# || -z "$line" ]]; then
                continue
            fi

            # Parse key-value pairs
            if [[ "$line" =~ ^[[:space:]]*([^=]+)=(.*)$ ]]; then
                key="${BASH_REMATCH[1]}"
                value="${BASH_REMATCH[2]}"

                # Remove surrounding quotes if any
                value="${value%\"}"
                value="${value#\"}"
                value="${value%\'}"
                value="${value#\'}"

                export "$key"="$value"
                echo "Exported: $key"
            fi
        done < "$env_file"
    done < <(find "$project_root" -type f -name ".env")
}

# Call the function
source_all_envs_and_export "./"
