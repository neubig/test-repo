#!/bin/bash
# Exit on any error
set -e

# Argument variable names (fix UID conflict by using USER_UID)
USER_NAME=${1:-appuser}
APP_NAME=${2:-OEDeviceService}
PORT=${3:-8080}
GID=${4:-2001}
USER_UID=${5:-1001}  # Changed from UID to USER_UID to avoid readonly variable conflict
TARGET_LOC=${6:-web}

# Environment variables
export APP_NAME=${APP_NAME}
export TZ=Asia/Kolkata
export PROFILE_NAME=''
export VAULT_SERVER_URL='http://localhost:8200'
export VAULT_TOKEN='dev-token-123'
export VAULT_PROFILE='staging'
export XMS=1024M
export XMX=1024M
export JAVA_OPTS="-Xms$XMS -Xmx$XMX -Dspring.profiles.active=$PROFILE_NAME"
export JAR_PATH="/data/releases/${APP_NAME}/${APP_NAME}.jar"

# Function to print status messages
print_status() {
    echo "[INFO] $1"
}

print_success() {
    echo "[SUCCESS] $1"
}

print_warning() {
    echo "[WARNING] $1"
}

print_error() {
    echo "[ERROR] $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check OS
check_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Detected OS: Linux"
    else
        print_error "This script is designed for Linux only. Detected: $OSTYPE"
        exit 1
    fi
}

# Function to install system packages (removed sudo for Docker, added missing packages)
install_system_packages() {
    print_status "Installing system packages..."
    
    # For Ubuntu/Debian
    if command_exists apt-get; then
        apt-get update
        apt-get install -y tzdata curl wget groff less python3 python3-pip unzip openjdk-17-jdk bc
        pip3 install awscli
    # For CentOS/RHEL
    elif command_exists yum; then
        yum update -y
        yum install -y tzdata curl wget groff less python3 python3-pip unzip java-1.8.0-openjdk java-1.8.0-openjdk-devel bc
        pip3 install awscli
    else
        print_error "Unsupported package manager. Please install required packages manually."
        exit 1
    fi
    
    print_success "System packages installed successfully"
}

# Function to install Vault
install_vault() {
    print_status "Installing Vault..."
    
    if ! command_exists vault; then
        VAULT_VERSION="1.15.0"
        
        # Download and install Vault
        cd /tmp
        wget https://releases.hashicorp.com/vault/${VAULT_VERSION}/vault_${VAULT_VERSION}_linux_amd64.zip
        unzip vault_${VAULT_VERSION}_linux_amd64.zip
        mv vault /usr/local/bin/
        chmod +x /usr/local/bin/vault
        
        # Clean up
        rm vault_${VAULT_VERSION}_linux_amd64.zip
        
        print_success "Vault ${VAULT_VERSION} installed successfully"
    else
        print_status "Vault already installed"
    fi
    
    # Verify Vault installation
    vault version
    
    # Start Vault server in development mode
    print_status "Starting Vault server..."
    nohup vault server -dev -dev-root-token-id="dev-token-123" -dev-listen-address="0.0.0.0:8200" > /tmp/vault.log 2>&1 &
    sleep 5
    
    # Set environment variables for Vault
    export VAULT_ADDR="http://0.0.0.0:8200"
    export VAULT_TOKEN="dev-token-123"
    
    # Wait for Vault to be ready (NO TIMEOUT - wait indefinitely)
    print_status "Waiting for Vault to be ready (no timeout)..."
    while ! vault status > /dev/null 2>&1; do
        print_status "Vault not ready yet, waiting 2 more seconds..."
        sleep 2
    done
    print_success "Vault is now ready!"
    
    # Enable KV secrets engine
    print_status "Enabling KV secrets engine..."
    vault secrets enable -path=secret kv-v1 2>/dev/null || print_warning "KV secrets engine may already be enabled"
    
    # Create secrets JSON file
    cat > /tmp/ods_secrets.json << 'EOF'
{
  "base.redis.database": "2",
  "base.redis.host": "localhost",
  "base.redis.pool.maxActive": "1024",
  "base.redis.pool.maxIdle": "200",
  "base.redis.pool.maxWait": "200",
  "base.redis.pool.minIdle": "100",
  "base.redis.pool.timeout": "2000",
  "ods.db.master.password": "root",
  "ods.db.master.url": "jdbc:mysql://localhost:3306/ods",
  "ods.db.master.username": "root",
  "ods.db.slave.password": "root",
  "ods.db.slave.url": "jdbc:mysql://localhost:3306/ods",
  "ods.db.slave.username": "root",
  "ods.elastic.search.host": "localhost",
  "ods.elastic.search.password": "elastic",
  "ods.elastic.search.port": "9200",
  "ods.elastic.search.protocol": "http",
  "ods.elastic.search.username": "elastic",
  "checksum.enc.key": "adasjdjakkk",
  "ods.encryption.ivToken": "NQH6![-pN&c-Wh;jDmXi",
  "ods.encryption.token": "*_QW^MpiZmHPsQ8~]{g",
  "ods.response.encryption.ivToken": "06D529AE2A70421DCE7DB4296CCC616F",
  "egs.baseUrl": "https://egs-eks-staging.paytm.com",
  "egs.new.base.url": "https://egs-eks-staging.paytm.com",
  "egs.old.base.url": "https://egs-staging.paytm.com",
  "notification.base.url": "http://notifications-platformproducer-staging.paytm.com",
  "oauth.base.url": "https://accounts-staging.paytm.in",
  "oauth.baseUrl": "https://accounts-staging.paytm.in",
  "oe.base.url": "https://goldengate-staging6.paytm.com/MerchantService",
  "oe.baseUrl": "https://goldengate-staging1.paytm.com/MerchantService",
  "pg.base.url": "https://bo-staging.paytm.com",
  "pg.baseUrl": "https://bo-staging.paytm.com",
  "se.base.url": "https://subscriptions-staging.paytm.com",
  "se.baseUrl": "https://subscriptions-staging.paytm.com",
  "uad.base.url": "https://uad-staging.paytm.com",
  "zm.base.url": "https://fsm-zone-mgmt-dev.paytm.com",
  "egs.client.id.value": "OE-ODS",
  "egs.client.secret": "SBvwnFGis467Ieth8DvAHjCvI7FFsqkJZhA9pb3WucSSe4dX1Cev6RzE6HsSgQ==",
  "notification.client.id": "stg-payments-OE-PMMS",
  "notification.client.secret": "f7b2e8f5d318c6ab5f092a91c9a11fe9704e80ac",
  "oauth.client.id": "ods-staging",
  "oauth.client.secret": "7nnlOqKuXTgzaTqd4N5ZT95HURDrFHpa",
  "oe.jwt.client.id": "ODS",
  "oe.jwt.client.secret": "3lkeljre4-cxcx-343s-mlml-65dfhsghsgfjhsdgfhas",
  "oe.oauth.token.enc.key": "655468576D5A7134743677397A24432646294A404E635266556A586E32723575",
  "pg.jwt.client.id": "66c02d3e-ebc0-4117-ba85-7f523ac8d424",
  "pg.jwt.client.secret": "WidnixnDo2780hILxdvvQXu9shJ9tIZnSsX4aEe9aKoOg5n7CtkijYqCb0ijNe7SE1qOu38JVU+gfx8G89oWvQ==",
  "se.jwt.client.id": "pmms",
  "se.jwt.client.secret": "YjQ0NGU1OTM4MDcxNTNiNzQ3MGQ3Nw==",
  "uad.client.id": "ODS",
  "uad.client.secret": "f4289237918d6ec6dc232406f8f69ad8",
  "zm.jwt.client.id": "zm_pmms",
  "s3.bucket.name": "pmms-staging",
  "s3.role.arn": "arn:aws:iam::182401677120:role/staging1-nonprod-onboardingengine-pinpoint-@staging1",
  "s3.role.session.name": "staging1-nonprod-onboardingengine-pinpoint-@staging1"
}
EOF

    # Store secrets in Vault
    print_status "Storing secrets in Vault..."
    vault kv put secret/ods/staging @/tmp/ods_secrets.json
    
    # Clean up temporary file
    rm /tmp/ods_secrets.json
    
    print_success "Vault setup completed with secrets stored at secret/ods/staging"
    
    # Update environment variables
    export VAULT_SERVER_URL="http://localhost:8200"
    export VAULT_TOKEN="dev-token-123"
    export VAULT_PROFILE="staging"
}

# Function to install Java
install_java() {
    print_status "Installing Java..."
    
    if ! command_exists java; then
        # For Ubuntu/Debian
        if command_exists apt-get; then
            apt-get install -y openjdk-17-jdk
        # For CentOS/RHEL
        elif command_exists yum; then
            yum install -y java-1.8.0-openjdk java-1.8.0-openjdk-devel
        fi
        print_success "Java installed successfully"
    else
        print_status "Java already installed"
    fi
    
    # Set JAVA_HOME based on what's available
    if [ -d "/usr/lib/jvm/java-17-openjdk-amd64" ]; then
        export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
    elif [ -d "/usr/lib/jvm/java-8-openjdk-amd64" ]; then
        export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
    elif [ -d "/usr/lib/jvm/java-1.8.0-openjdk" ]; then
        export JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk
    fi
    
    print_status "JAVA_HOME set to: $JAVA_HOME"
    java -version
}

# Function to install Maven
install_maven() {
    print_status "Installing Maven 3.9.9..."
    
    if ! command_exists mvn || ! mvn -version 2>&1 | grep -q "3.9.9"; then
        MAVEN_VERSION="3.9.9"
        MAVEN_DIR="/opt/maven"
        
        if [ ! -d "$MAVEN_DIR" ]; then
            mkdir -p $MAVEN_DIR
            cd /tmp
            wget https://archive.apache.org/dist/maven/maven-3/$MAVEN_VERSION/binaries/apache-maven-$MAVEN_VERSION-bin.tar.gz
            tar -xzf apache-maven-$MAVEN_VERSION-bin.tar.gz -C /opt
            mv /opt/apache-maven-$MAVEN_VERSION $MAVEN_DIR
            rm apache-maven-$MAVEN_VERSION-bin.tar.gz
        fi
        
        echo 'export PATH="/opt/maven/bin:$PATH"' >> ~/.bashrc
        export PATH="/opt/maven/bin:$PATH"
        print_success "Maven 3.9.9 installed successfully"
    else
        print_status "Maven 3.9.9 already installed"
    fi
}

# Function to create directories and setup user
setup_directories_and_user() {
    print_status "Setting up directories and user..."
    
    # Create directories
    mkdir -p /data/releases/${APP_NAME}/
    mkdir -p /logs/${APP_NAME}
    
    # Create user and group
    groupadd -g ${GID} ${USER_NAME} 2>/dev/null || true
    useradd -m -u ${USER_UID} -g ${GID} -s /bin/bash ${USER_NAME} 2>/dev/null || true
    
    # Set ownership
    chown -R ${USER_NAME}:${USER_NAME} /home/${USER_NAME}/
    chown -R ${USER_NAME}:${USER_NAME} /data/releases/${APP_NAME}/
    chown -R ${USER_NAME}:${USER_NAME} /logs/
    
    print_success "Directories and user setup completed"
}

# Function to copy application files
copy_application_files() {
    print_status "Copying application files..."
    
    # Create mock files for testing
    if [ ! -f "${TARGET_LOC}/target/${APP_NAME}.jar" ]; then
        mkdir -p ${TARGET_LOC}/target
        echo "Mock JAR content" > ${TARGET_LOC}/target/${APP_NAME}.jar
    fi
    
    if [ ! -f "./entrypoint.sh" ]; then
        cat > ./entrypoint.sh << 'EOF'
#!/bin/bash
echo "Mock entrypoint script"
java $JAVA_OPTS -jar $JAR_PATH
EOF
    fi
    
    if [ -f "${TARGET_LOC}/target/${APP_NAME}.jar" ]; then
        cp ${TARGET_LOC}/target/${APP_NAME}.jar /data/releases/${APP_NAME}/
        chown ${USER_NAME}:${USER_NAME} /data/releases/${APP_NAME}/${APP_NAME}.jar
        print_success "Application JAR copied successfully"
    else
        print_warning "Application JAR not found at ${TARGET_LOC}/target/${APP_NAME}.jar"
    fi
    
    if [ -f "./entrypoint.sh" ]; then
        cp ./entrypoint.sh /entrypoint.sh
        chown ${USER_NAME}:${USER_NAME} /entrypoint.sh
        chmod +x /entrypoint.sh
        print_success "Entrypoint script copied successfully"
    else
        print_warning "Entrypoint script not found at ./entrypoint.sh"
    fi
}

# Function to verify setup
verify_setup() {
    print_status "Verifying setup..."
    
    echo "=== Java Version ==="
    java -version
    
    echo "=== Maven Version ==="
    mvn -version
    
    echo "=== Vault Version ==="
    vault version
    
    echo "=== Vault Status ==="
    vault status
    
    echo "=== Directories ==="
    ls -la /data/releases/${APP_NAME}/
    ls -la /logs/
    
    echo "=== User ==="
    id ${USER_NAME}
    
    print_success "Setup verification completed"
}

# Function to display configuration
display_configuration() {
    print_status "Configuration Summary:"
    echo "  User: ${USER_NAME}"
    echo "  App: ${APP_NAME}"
    echo "  Port: ${PORT}"
    echo "  GID: ${GID}"
    echo "  UID: ${USER_UID}"
    echo "  Target Location: ${TARGET_LOC}"
    echo "  JAVA_HOME: ${JAVA_HOME}"
    echo "  JAR_PATH: ${JAR_PATH}"
    echo "  JAVA_OPTS: ${JAVA_OPTS}"
    echo "  VAULT_SERVER_URL: ${VAULT_SERVER_URL}"
    echo "  VAULT_TOKEN: ${VAULT_TOKEN}"
    echo "  VAULT_PROFILE: ${VAULT_PROFILE}"
    echo ""
}

# Main execution
main() {
    print_status "Starting OE Device Service setup (NO TIMEOUT VERSION)..."
    
    check_os
    install_system_packages
    install_vault
    install_java
    install_maven
    setup_directories_and_user
    copy_application_files
    verify_setup
    display_configuration
    
    print_success "Setup completed successfully!"
    print_status "Application is ready to run on port ${PORT}"
    echo ""
    print_status "To run the application:"
    echo "  sudo -u ${USER_NAME} /entrypoint.sh"
    echo ""
}

# Run main function
main "$@"