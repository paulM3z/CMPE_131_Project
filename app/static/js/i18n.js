(function () {
  const html = document.documentElement;
  const lang = (html.getAttribute('lang') || 'en').toLowerCase();
  if (lang === 'en') return;

  const dictionaries = {
    es: {
      'Dashboard': 'Panel',
      'Clubs': 'Clubes',
      'Events': 'Eventos',
      'Settings': 'Configuracion',
      'Sign Out': 'Cerrar sesion',
      'Account Settings': 'Configuracion de cuenta',
      'Manage your profile and preferences.': 'Administra tu perfil y preferencias.',
      'Profile': 'Perfil',
      'Profile Photo': 'Foto de perfil',
      'Choose image': 'Elegir imagen',
      'Upload Photo': 'Subir foto',
      'Username': 'Usuario',
      'Email Address': 'Correo electronico',
      'Phone Number': 'Numero de telefono',
      'Update': 'Actualizar',
      'Security': 'Seguridad',
      'Change Password': 'Cambiar contrasena',
      'Current Password': 'Contrasena actual',
      'New Password': 'Nueva contrasena',
      'Confirm New Password': 'Confirmar nueva contrasena',
      'Preferences': 'Preferencias',
      'Display & Language': 'Pantalla e idioma',
      'Language': 'Idioma',
      'Theme': 'Tema',
      'Text Size': 'Tamano del texto',
      'Small': 'Pequeno',
      'Medium': 'Mediano',
      'Large': 'Grande',
      'Save Preferences': 'Guardar preferencias',
      'Account Info': 'Informacion de cuenta',
      'Account ID': 'ID de cuenta',
      'Role': 'Rol',
      'Member Since': 'Miembro desde',
      'Student': 'Estudiante',
      'Administrator': 'Administrador',
      'Create Event': 'Crear evento',
      'Create a New Event': 'Crear un nuevo evento',
      'Event Title': 'Titulo del evento',
      'Date': 'Fecha',
      'Time': 'Hora',
      'Location': 'Ubicacion',
      'Description': 'Descripcion',
      'Capacity': 'Capacidad',
      'Hosting Club': 'Club anfitrion',
      'Tags': 'Etiquetas',
      'Visibility': 'Visibilidad',
      'Cancel': 'Cancelar',
      'Save Changes': 'Guardar cambios',
      'RSVP to This Event': 'Confirmar asistencia',
      'Cancel RSVP': 'Cancelar RSVP'
    },
    fr: {
      'Dashboard': 'Tableau de bord',
      'Clubs': 'Clubs',
      'Events': 'Evenements',
      'Settings': 'Parametres',
      'Sign Out': 'Se deconnecter',
      'Account Settings': 'Parametres du compte',
      'Profile': 'Profil',
      'Username': "Nom d'utilisateur",
      'Email Address': 'Adresse e-mail',
      'Phone Number': 'Numero de telephone',
      'Security': 'Securite',
      'Preferences': 'Preferences',
      'Language': 'Langue',
      'Account Info': 'Infos du compte',
      'Account ID': 'ID du compte',
      'Role': 'Role',
      'Student': 'Etudiant',
      'Member Since': 'Membre depuis',
      'Save Preferences': 'Enregistrer'
    },
    de: {
      'Dashboard': 'Ubersicht',
      'Clubs': 'Clubs',
      'Events': 'Veranstaltungen',
      'Settings': 'Einstellungen',
      'Sign Out': 'Abmelden',
      'Account Settings': 'Kontoeinstellungen',
      'Profile': 'Profil',
      'Username': 'Benutzername',
      'Email Address': 'E-Mail-Adresse',
      'Phone Number': 'Telefonnummer',
      'Preferences': 'Einstellungen',
      'Language': 'Sprache',
      'Account Info': 'Kontoinfo',
      'Account ID': 'Konto-ID',
      'Role': 'Rolle',
      'Student': 'Student',
      'Member Since': 'Mitglied seit',
      'Save Preferences': 'Speichern'
    },
    pt: {
      'Dashboard': 'Painel',
      'Clubs': 'Clubes',
      'Events': 'Eventos',
      'Settings': 'Configuracoes',
      'Sign Out': 'Sair',
      'Account Settings': 'Configuracoes da conta',
      'Profile': 'Perfil',
      'Username': 'Usuario',
      'Email Address': 'E-mail',
      'Phone Number': 'Telefone',
      'Preferences': 'Preferencias',
      'Language': 'Idioma',
      'Account Info': 'Informacoes da conta',
      'Account ID': 'ID da conta',
      'Role': 'Funcao',
      'Student': 'Estudante',
      'Member Since': 'Membro desde',
      'Save Preferences': 'Salvar preferencias'
    },
    zh: {
      'Dashboard': '仪表板',
      'Clubs': '社团',
      'Events': '活动',
      'Settings': '设置',
      'Sign Out': '退出',
      'Account Settings': '账户设置',
      'Profile': '个人资料',
      'Username': '用户名',
      'Email Address': '电子邮件',
      'Phone Number': '电话号码',
      'Preferences': '偏好设置',
      'Language': '语言',
      'Account Info': '账户信息',
      'Account ID': '账户 ID',
      'Role': '角色',
      'Student': '学生',
      'Member Since': '加入时间',
      'Save Preferences': '保存偏好'
    },
    ja: {
      'Dashboard': 'ダッシュボード',
      'Clubs': 'クラブ',
      'Events': 'イベント',
      'Settings': '設定',
      'Sign Out': 'サインアウト',
      'Account Settings': 'アカウント設定',
      'Profile': 'プロフィール',
      'Username': 'ユーザー名',
      'Email Address': 'メール',
      'Phone Number': '電話番号',
      'Preferences': '設定',
      'Language': '言語',
      'Account Info': 'アカウント情報',
      'Account ID': 'アカウント ID',
      'Role': '役割',
      'Student': '学生',
      'Member Since': '登録日',
      'Save Preferences': '保存'
    },
    ko: {
      'Dashboard': '대시보드',
      'Clubs': '동아리',
      'Events': '이벤트',
      'Settings': '설정',
      'Sign Out': '로그아웃',
      'Account Settings': '계정 설정',
      'Profile': '프로필',
      'Username': '사용자 이름',
      'Email Address': '이메일',
      'Phone Number': '전화번호',
      'Preferences': '환경설정',
      'Language': '언어',
      'Account Info': '계정 정보',
      'Account ID': '계정 ID',
      'Role': '역할',
      'Student': '학생',
      'Member Since': '가입일',
      'Save Preferences': '저장'
    },
    ar: {
      'Dashboard': 'لوحة التحكم',
      'Clubs': 'النوادي',
      'Events': 'الفعاليات',
      'Settings': 'الإعدادات',
      'Sign Out': 'تسجيل الخروج',
      'Account Settings': 'إعدادات الحساب',
      'Profile': 'الملف الشخصي',
      'Username': 'اسم المستخدم',
      'Email Address': 'البريد الإلكتروني',
      'Phone Number': 'رقم الهاتف',
      'Preferences': 'التفضيلات',
      'Language': 'اللغة',
      'Account Info': 'معلومات الحساب',
      'Account ID': 'معرف الحساب',
      'Role': 'الدور',
      'Student': 'طالب',
      'Member Since': 'عضو منذ',
      'Save Preferences': 'حفظ التفضيلات'
    }
  };

  const dictionary = dictionaries[lang];
  if (!dictionary) return;
  if (lang === 'ar') {
    html.setAttribute('dir', 'rtl');
  }

  const SKIP_TAGS = new Set(['SCRIPT', 'STYLE', 'TEXTAREA', 'INPUT', 'SELECT']);

  function translateTextNode(node) {
    const original = node.nodeValue;
    const trimmed = original.trim();
    if (!trimmed) return;
    if (dictionary[trimmed]) {
      node.nodeValue = original.replace(trimmed, dictionary[trimmed]);
      return;
    }

    let translated = trimmed;
    Object.keys(dictionary)
      .sort((a, b) => b.length - a.length)
      .forEach((key) => {
        translated = translated.replaceAll(key, dictionary[key]);
      });
    if (translated !== trimmed) {
      node.nodeValue = original.replace(trimmed, translated);
    }
  }

  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
    acceptNode(node) {
      return node.parentElement && !SKIP_TAGS.has(node.parentElement.tagName)
        ? NodeFilter.FILTER_ACCEPT
        : NodeFilter.FILTER_REJECT;
    }
  });

  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  nodes.forEach(translateTextNode);
})();
