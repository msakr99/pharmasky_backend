#!/bin/bash

# 🔑 SSH Setup Script for PharmasSky Deployment
# إعداد SSH key للنشر التلقائي

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Server info from server-config.md
DROPLET_IP="129.212.140.152"
DROPLET_USER="root"
SSH_KEY_PATH="$HOME/.ssh/pharmasky-github-deploy"
SSH_PUB_KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICiYHpODLkXsNKxolkjyIN6xWhWULWKnvL8cyNaNr+Jp pharmasky-github-deploy"

echo -e "${BLUE}🔑 إعداد SSH Key للنشر التلقائي${NC}"
echo -e "${BLUE}===================================${NC}"
echo

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}📋 $1${NC}"
}

# Check if SSH directory exists
if [ ! -d "$HOME/.ssh" ]; then
    print_info "إنشاء مجلد SSH..."
    mkdir -p "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"
fi

# Check if key already exists
if [ -f "$SSH_KEY_PATH" ]; then
    print_warning "SSH key موجود بالفعل في: $SSH_KEY_PATH"
    read -p "هل تريد إعادة إنشائه؟ (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "استخدام المفتاح الموجود"
    else
        rm -f "$SSH_KEY_PATH" "$SSH_KEY_PATH.pub"
        print_info "تم حذف المفتاح القديم"
    fi
fi

# Generate SSH key if not exists
if [ ! -f "$SSH_KEY_PATH" ]; then
    print_info "إنشاء SSH key جديد..."
    ssh-keygen -t ed25519 -f "$SSH_KEY_PATH" -C "pharmasky-github-deploy" -N ""
    if [ $? -eq 0 ]; then
        print_success "تم إنشاء SSH key"
    else
        print_error "فشل في إنشاء SSH key"
        exit 1
    fi
fi

# Set correct permissions
chmod 600 "$SSH_KEY_PATH"
chmod 644 "$SSH_KEY_PATH.pub"
print_success "تم تعيين الصلاحيات الصحيحة"

# Display public key
echo
print_info "المفتاح العام (يجب إضافته للسيرفر):"
echo -e "${YELLOW}$(cat $SSH_KEY_PATH.pub)${NC}"
echo

# Check if key matches the one in server-config.md
CURRENT_PUB_KEY=$(cat "$SSH_KEY_PATH.pub")
if [ "$CURRENT_PUB_KEY" = "$SSH_PUB_KEY" ]; then
    print_success "المفتاح يطابق المفتاح في server-config.md"
else
    print_warning "المفتاح لا يطابق المفتاح في server-config.md"
    echo "المفتاح المطلوب:"
    echo -e "${BLUE}$SSH_PUB_KEY${NC}"
    echo
    echo "المفتاح الحالي:"
    echo -e "${YELLOW}$CURRENT_PUB_KEY${NC}"
    echo
    print_info "ستحتاج لإضافة المفتاح الجديد للسيرفر يدوياً"
fi

# Test SSH connection
print_info "اختبار الاتصال بالسيرفر..."
if ssh -i "$SSH_KEY_PATH" -o ConnectTimeout=10 -o BatchMode=yes "$DROPLET_USER@$DROPLET_IP" 'echo "SSH connection successful"' 2>/dev/null; then
    print_success "الاتصال SSH يعمل بشكل صحيح!"
else
    print_error "فشل الاتصال SSH"
    echo
    print_info "لإضافة المفتاح للسيرفر، قم بأحد الطرق التالية:"
    echo
    echo "الطريقة الأولى - استخدام ssh-copy-id:"
    echo -e "${BLUE}ssh-copy-id -i $SSH_KEY_PATH.pub $DROPLET_USER@$DROPLET_IP${NC}"
    echo
    echo "الطريقة الثانية - نسخ المفتاح يدوياً:"
    echo "1. اتصل بالسيرفر:"
    echo -e "${BLUE}ssh $DROPLET_USER@$DROPLET_IP${NC}"
    echo
    echo "2. أضف المفتاح العام:"
    echo -e "${BLUE}echo \"$(cat $SSH_KEY_PATH.pub)\" >> ~/.ssh/authorized_keys${NC}"
    echo -e "${BLUE}chmod 600 ~/.ssh/authorized_keys${NC}"
    echo -e "${BLUE}chmod 700 ~/.ssh${NC}"
    echo
fi

# Add key to SSH agent
print_info "إضافة المفتاح لـ SSH agent..."
if command -v ssh-add >/dev/null 2>&1; then
    ssh-add "$SSH_KEY_PATH" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_success "تم إضافة المفتاح لـ SSH agent"
    else
        print_warning "فشل إضافة المفتاح لـ SSH agent (قد لا يكون مطلوباً)"
    fi
else
    print_warning "ssh-add غير متوفر"
fi

echo
print_success "تم الانتهاء من إعداد SSH!"
echo
print_info "الخطوات التالية:"
echo "1. تأكد من أن SSH يعمل بتشغيل: ./setup_deployment.sh"
echo "2. استخدم للنشر السريع: ./auto_deploy.sh"
echo "3. أو استخدم للنشر المفصل: ./update_and_deploy.sh"
