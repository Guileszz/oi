#!/bin/bash
###############################################################################
# Full Architecture Audit Script
# Automatiza: Clone de 78 repos privados + mapper.py + análise completa
###############################################################################

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
AUDIT_DIR="${1:-./../repos_audit}"
GITHUB_USER="Guileszz"
MAX_REPOS=100

###############################################################################
# Helper Functions
###############################################################################

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

###############################################################################
# Step 1: Verify Prerequisites
###############################################################################

verify_prerequisites() {
    print_header "Step 1: Verificando Prerequisites"
    
    # Check GitHub CLI
    if ! command -v gh &> /dev/null; then
        print_error "GitHub CLI não está instalada"
        echo "Instale em: https://cli.github.com/"
        exit 1
    fi
    print_success "GitHub CLI instalada"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 não está instalada"
        exit 1
    fi
    print_success "Python 3 instalada: $(python3 --version)"
    
    # Check Git
    if ! command -v git &> /dev/null; then
        print_error "Git não está instalada"
        exit 1
    fi
    print_success "Git instalada: $(git --version)"
    
    # Verify GitHub authentication
    if ! gh auth status &> /dev/null; then
        print_error "Não autenticado no GitHub"
        echo "Execute: gh auth login"
        exit 1
    fi
    print_success "Autenticado no GitHub"
    echo
}

###############################################################################
# Step 2: Create Audit Directory
###############################################################################

setup_audit_directory() {
    print_header "Step 2: Preparando Diretório de Auditoria"
    
    if [ -d "$AUDIT_DIR" ]; then
        print_warning "Diretório $AUDIT_DIR já existe"
        read -p "Deseja continuar (alguns repos podem já estar clonados)? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        mkdir -p "$AUDIT_DIR"
        print_success "Diretório criado: $AUDIT_DIR"
    fi
    
    cd "$AUDIT_DIR"
    print_success "Diretório atual: $(pwd)"
    echo
}

###############################################################################
# Step 3: Fetch Repository List
###############################################################################

fetch_repo_list() {
    print_header "Step 3: Buscando Lista de Repositórios Privados"
    
    # Fetch all private repos
    REPOS=$(gh repo list "$GITHUB_USER" \
        --limit $MAX_REPOS \
        --visibility private \
        --json nameWithOwner \
        -q '.[].nameWithOwner')
    
    REPO_COUNT=$(echo "$REPOS" | wc -l)
    print_success "Encontrados $REPO_COUNT repositórios privados"
    
    if [ $REPO_COUNT -eq 0 ]; then
        print_error "Nenhum repositório privado encontrado"
        exit 1
    fi
    
    echo "$REPOS"
    echo
}

###############################################################################
# Step 4: Clone All Repositories
###############################################################################

clone_all_repos() {
    print_header "Step 4: Clonando Repositórios (Depth=1 para velocidade)"
    
    local repos="$1"
    local total=$(echo "$repos" | wc -l)
    local current=0
    
    echo "$repos" | while read -r repo; do
        current=$((current + 1))
        
        # Extract repo name
        repo_name=$(echo "$repo" | cut -d'/' -f2)
        
        if [ -d "$repo_name" ]; then
            print_warning "[$current/$total] $repo_name já existe, pulando..."
        else
            print_warning "[$current/$total] Clonando $repo..."
            if gh repo clone "$repo" -- --depth 1 --quiet 2>/dev/null; then
                print_success "[$current/$total] $repo_name clonado"
            else
                print_error "[$current/$total] Falha ao clonar $repo"
            fi
        fi
    done
    
    echo
}

###############################################################################
# Step 5: Copy Mapper Script
###############################################################################

copy_mapper_script() {
    print_header "Step 5: Preparando Mapper Script"
    
    # Get the directory where this script is located
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    MAPPER_SRC="$SCRIPT_DIR/mapper.py"
    MAPPER_DEST="$AUDIT_DIR/mapper.py"
    
    if [ ! -f "$MAPPER_SRC" ]; then
        print_error "mapper.py não encontrado em: $MAPPER_SRC"
        print_warning "Tentando usar mapper.py do diretório atual..."
        
        if [ ! -f "$AUDIT_DIR/mapper.py" ]; then
            print_error "mapper.py não encontrado. Execute este script do diretório com mapper.py"
            exit 1
        fi
    else
        cp "$MAPPER_SRC" "$MAPPER_DEST"
        print_success "mapper.py copiado para: $MAPPER_DEST"
    fi
    
    chmod +x "$MAPPER_DEST"
    print_success "Permissões ajustadas"
    echo
}

###############################################################################
# Step 6: Run Mapper Script
###############################################################################

run_mapper() {
    print_header "Step 6: Executando Architecture Mapper (ISO ⏳)"
    
    cd "$AUDIT_DIR"
    
    if [ ! -f "mapper.py" ]; then
        print_error "mapper.py não encontrado em: $AUDIT_DIR"
        exit 1
    fi
    
    print_warning "Iniciando análise... isto pode levar alguns minutos..."
    python3 mapper.py
    
    echo
}

###############################################################################
# Step 7: Verify Outputs
###############################################################################

verify_outputs() {
    print_header "Step 7: Verificando Outputs Gerados"
    
    cd "$AUDIT_DIR"
    
    if [ -f "architecture_map.json" ]; then
        LINES=$(wc -l < architecture_map.json)
        SIZE=$(du -h architecture_map.json | cut -f1)
        print_success "architecture_map.json gerado ($SIZE, $LINES linhas)"
    else
        print_error "architecture_map.json não gerado"
        exit 1
    fi
    
    if [ -f "convergence_matrix.md" ]; then
        LINES=$(wc -l < convergence_matrix.md)
        print_success "convergence_matrix.md gerado ($LINES linhas)"
    else
        print_error "convergence_matrix.md não gerado"
        exit 1
    fi
    
    echo
}

###############################################################################
# Step 8: Summary & Next Steps
###############################################################################

print_summary() {
    print_header "✅ AUDITORIA COMPLETA!"
    
    echo -e "${GREEN}Arquivos gerados em: $AUDIT_DIR${NC}"
    echo
    echo "📋 Arquivos criados:"
    echo "  1. architecture_map.json    - Mapa completo da arquitetura"
    echo "  2. convergence_matrix.md    - Tabela de convergência"
    echo
    echo "🔧 Próximos passos:"
    echo "  1. Revise os outputs:"
    echo "     cat $AUDIT_DIR/architecture_map.json | jq ."
    echo "     cat $AUDIT_DIR/convergence_matrix.md"
    echo
    echo "  2. Aplique a refatoração ('Lucrative Necromancy'):"
    echo "     - Compartilhe os arquivos com o Copilot"
    echo "     - Use o protocolo de análise de redundância"
    echo
    echo "📊 Estatísticas:"
    echo "  - Diretório: $AUDIT_DIR"
    echo "  - Repositórios analisados: $(ls -d */ 2>/dev/null | wc -l)"
    echo
    print_success "Audit completo!"
}

###############################################################################
# Main Execution Flow
###############################################################################

main() {
    print_header "🏗️  FULL ARCHITECTURE AUDIT PIPELINE"
    echo "Automatizando clone + análise de 78 repositórios privados"
    echo
    
    # Execute all steps
    verify_prerequisites
    setup_audit_directory
    REPO_LIST=$(fetch_repo_list)
    clone_all_repos "$REPO_LIST"
    copy_mapper_script
    run_mapper
    verify_outputs
    print_summary
}

# Run main function
main "$@"
