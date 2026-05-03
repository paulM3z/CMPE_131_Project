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
      'Log In': 'Iniciar sesion',
      'Sign Up': 'Registrarse',
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
      'Campus Events': 'Eventos del campus',
      "Discover what's happening around campus.": 'Descubre lo que pasa en el campus.',
      'Create Event': 'Crear evento',
      'Create an Event': 'Crear un evento',
      'Create a New Event': 'Crear un nuevo evento',
      'Edit Event': 'Editar evento',
      'Event Title': 'Titulo del evento',
      'Date': 'Fecha',
      'Time': 'Hora',
      'Location': 'Ubicacion',
      'Google Maps Location': 'Ubicacion de Google Maps',
      'Description': 'Descripcion',
      'Capacity': 'Capacidad',
      'Hosting Club': 'Club anfitrion',
      'Tags': 'Etiquetas',
      'Visibility': 'Visibilidad',
      'Private event': 'Evento privado',
      'Cancel': 'Cancelar',
      'Save Changes': 'Guardar cambios',
      'Details': 'Detalles',
      'RSVP': 'Confirmar asistencia',
      'RSVP to This Event': 'Confirmar asistencia a este evento',
      'Cancel RSVP': 'Cancelar asistencia',
      'Open in Google Maps': 'Abrir en Google Maps',
      'About This Event': 'Acerca de este evento',
      'Event Details': 'Detalles del evento',
      'Attendees': 'Asistentes',
      'Organizer': 'Organizador',
      'Hosted by': 'Organizado por',
      'Campus Clubs': 'Clubes del campus',
      'Find your community.': 'Encuentra tu comunidad.',
      'Create Club': 'Crear club',
      'Join Club': 'Unirse al club',
      'Leave Club': 'Salir del club',
      'Club Events': 'Eventos del club',
      'Members': 'Miembros',
      'About': 'Acerca de',
      'Visibility': 'Visibilidad',
      'Private': 'Privado',
      'Public': 'Publico'
    },
    fr: {
      'Dashboard': 'Tableau de bord',
      'Clubs': 'Clubs',
      'Events': 'Evenements',
      'Settings': 'Parametres',
      'Sign Out': 'Se deconnecter',
      'Log In': 'Connexion',
      'Sign Up': "S'inscrire",
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
      'Save Preferences': 'Enregistrer les preferences',
      'Create Event': 'Creer un evenement',
      'Event Title': "Titre de l'evenement",
      'Date': 'Date',
      'Time': 'Heure',
      'Location': 'Lieu',
      'Description': 'Description',
      'Capacity': 'Capacite',
      'Open in Google Maps': 'Ouvrir dans Google Maps'
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
      'Save Preferences': 'Speichern',
      'Create Event': 'Veranstaltung erstellen',
      'Date': 'Datum',
      'Time': 'Zeit',
      'Location': 'Ort',
      'Description': 'Beschreibung',
      'Capacity': 'Kapazitat',
      'Open in Google Maps': 'In Google Maps offnen'
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
      'Save Preferences': 'Salvar preferencias',
      'Create Event': 'Criar evento',
      'Open in Google Maps': 'Abrir no Google Maps'
    },
    zh: {
      'Dashboard': '仪表板',
      'Clubs': '社团',
      'Events': '活动',
      'Settings': '设置',
      'Sign Out': '退出',
      'Log In': '登录',
      'Sign Up': '注册',
      'Account Settings': '账户设置',
      'Manage your profile and preferences.': '管理你的个人资料和偏好设置。',
      'Profile': '个人资料',
      'Profile Photo': '个人照片',
      'Choose image': '选择图片',
      'Upload Photo': '上传照片',
      'Username': '用户名',
      'Email Address': '电子邮件地址',
      'Phone Number': '电话号码',
      'Update': '更新',
      'Security': '安全',
      'Change Password': '更改密码',
      'Current Password': '当前密码',
      'New Password': '新密码',
      'Confirm New Password': '确认新密码',
      'Preferences': '偏好设置',
      'Display & Language': '显示和语言',
      'Language': '语言',
      'Theme': '主题',
      'Text Size': '文字大小',
      'Small': '小',
      'Medium': '中',
      'Large': '大',
      'Save Preferences': '保存偏好设置',
      'Account Info': '账户信息',
      'Account ID': '账户 ID',
      'Role': '角色',
      'Member Since': '加入时间',
      'Student': '学生',
      'Administrator': '管理员',
      'Campus Events': '校园活动',
      "Discover what's happening around campus.": '发现校园里的活动。',
      'Create Event': '创建活动',
      'Create an Event': '创建活动',
      'Create a New Event': '创建新活动',
      'Edit Event': '编辑活动',
      'Event Title': '活动标题',
      'Date': '日期',
      'Time': '时间',
      'Location': '地点',
      'Google Maps Location': 'Google 地图位置',
      'Description': '描述',
      'Capacity': '容量',
      'Hosting Club': '主办社团',
      'Tags': '标签',
      'Visibility': '可见性',
      'Private event': '私人活动',
      'Cancel': '取消',
      'Save Changes': '保存更改',
      'Details': '详情',
      'RSVP': ' RSVP',
      'RSVP to This Event': '报名参加此活动',
      'Cancel RSVP': '取消报名',
      'Open in Google Maps': '在 Google 地图中打开',
      'About This Event': '关于此活动',
      'Event Details': '活动详情',
      'Attendees': '参加者',
      'Organizer': '组织者',
      'Hosted by': '主办方',
      'Campus Clubs': '校园社团',
      'Find your community.': '找到你的社区。',
      'Create Club': '创建社团',
      'Join Club': '加入社团',
      'Leave Club': '退出社团',
      'Club Events': '社团活动',
      'Members': '成员',
      'About': '关于',
      'Private': '私密',
      'Public': '公开'
    },
    ja: {
      'Dashboard': 'ダッシュボード',
      'Clubs': 'クラブ',
      'Events': 'イベント',
      'Settings': '設定',
      'Sign Out': 'サインアウト',
      'Log In': 'ログイン',
      'Sign Up': '登録',
      'Account Settings': 'アカウント設定',
      'Manage your profile and preferences.': 'プロフィールと設定を管理します。',
      'Profile': 'プロフィール',
      'Profile Photo': 'プロフィール写真',
      'Choose image': '画像を選択',
      'Upload Photo': '写真をアップロード',
      'Username': 'ユーザー名',
      'Email Address': 'メールアドレス',
      'Phone Number': '電話番号',
      'Update': '更新',
      'Security': 'セキュリティ',
      'Change Password': 'パスワードを変更',
      'Current Password': '現在のパスワード',
      'New Password': '新しいパスワード',
      'Confirm New Password': '新しいパスワードを確認',
      'Preferences': '設定',
      'Display & Language': '表示と言語',
      'Language': '言語',
      'Theme': 'テーマ',
      'Text Size': '文字サイズ',
      'Small': '小',
      'Medium': '中',
      'Large': '大',
      'Save Preferences': '設定を保存',
      'Account Info': 'アカウント情報',
      'Account ID': 'アカウント ID',
      'Role': '役割',
      'Member Since': '登録日',
      'Student': '学生',
      'Administrator': '管理者',
      'Campus Events': 'キャンパスイベント',
      "Discover what's happening around campus.": 'キャンパスで起きていることを見つけましょう。',
      'Create Event': 'イベントを作成',
      'Create an Event': 'イベントを作成',
      'Create a New Event': '新しいイベントを作成',
      'Edit Event': 'イベントを編集',
      'Event Title': 'イベント名',
      'Date': '日付',
      'Time': '時間',
      'Location': '場所',
      'Google Maps Location': 'Google マップの場所',
      'Description': '説明',
      'Capacity': '定員',
      'Hosting Club': '主催クラブ',
      'Tags': 'タグ',
      'Visibility': '公開範囲',
      'Private event': '非公開イベント',
      'Cancel': 'キャンセル',
      'Save Changes': '変更を保存',
      'Details': '詳細',
      'RSVP': '参加登録',
      'RSVP to This Event': 'このイベントに参加登録',
      'Cancel RSVP': '参加登録をキャンセル',
      'Open in Google Maps': 'Google マップで開く',
      'About This Event': 'このイベントについて',
      'Event Details': 'イベント詳細',
      'Attendees': '参加者',
      'Organizer': '主催者',
      'Hosted by': '主催',
      'Campus Clubs': 'キャンパスクラブ',
      'Find your community.': 'あなたのコミュニティを見つけましょう。',
      'Create Club': 'クラブを作成',
      'Join Club': 'クラブに参加',
      'Leave Club': 'クラブを退会',
      'Club Events': 'クラブイベント',
      'Members': 'メンバー',
      'About': '概要',
      'Private': '非公開',
      'Public': '公開'
    },
    ko: {
      'Dashboard': '대시보드',
      'Clubs': '동아리',
      'Events': '이벤트',
      'Settings': '설정',
      'Sign Out': '로그아웃',
      'Log In': '로그인',
      'Sign Up': '가입',
      'Account Settings': '계정 설정',
      'Manage your profile and preferences.': '프로필과 환경설정을 관리하세요.',
      'Profile': '프로필',
      'Profile Photo': '프로필 사진',
      'Choose image': '이미지 선택',
      'Upload Photo': '사진 업로드',
      'Username': '사용자 이름',
      'Email Address': '이메일 주소',
      'Phone Number': '전화번호',
      'Update': '업데이트',
      'Security': '보안',
      'Change Password': '비밀번호 변경',
      'Current Password': '현재 비밀번호',
      'New Password': '새 비밀번호',
      'Confirm New Password': '새 비밀번호 확인',
      'Preferences': '환경설정',
      'Display & Language': '표시 및 언어',
      'Language': '언어',
      'Theme': '테마',
      'Text Size': '글자 크기',
      'Small': '작게',
      'Medium': '보통',
      'Large': '크게',
      'Save Preferences': '환경설정 저장',
      'Account Info': '계정 정보',
      'Account ID': '계정 ID',
      'Role': '역할',
      'Member Since': '가입일',
      'Student': '학생',
      'Administrator': '관리자',
      'Campus Events': '캠퍼스 이벤트',
      "Discover what's happening around campus.": '캠퍼스에서 열리는 일을 찾아보세요.',
      'Create Event': '이벤트 만들기',
      'Create an Event': '이벤트 만들기',
      'Create a New Event': '새 이벤트 만들기',
      'Edit Event': '이벤트 편집',
      'Event Title': '이벤트 제목',
      'Date': '날짜',
      'Time': '시간',
      'Location': '장소',
      'Google Maps Location': 'Google 지도 위치',
      'Description': '설명',
      'Capacity': '정원',
      'Hosting Club': '주최 동아리',
      'Tags': '태그',
      'Visibility': '공개 범위',
      'Private event': '비공개 이벤트',
      'Cancel': '취소',
      'Save Changes': '변경 사항 저장',
      'Details': '상세 정보',
      'RSVP': '참석 신청',
      'RSVP to This Event': '이 이벤트 참석 신청',
      'Cancel RSVP': '참석 신청 취소',
      'Open in Google Maps': 'Google 지도에서 열기',
      'About This Event': '이 이벤트 소개',
      'Event Details': '이벤트 세부 정보',
      'Attendees': '참석자',
      'Organizer': '주최자',
      'Hosted by': '주최',
      'Campus Clubs': '캠퍼스 동아리',
      'Find your community.': '나의 커뮤니티를 찾아보세요.',
      'Create Club': '동아리 만들기',
      'Join Club': '동아리 가입',
      'Leave Club': '동아리 탈퇴',
      'Club Events': '동아리 이벤트',
      'Members': '회원',
      'About': '소개',
      'Private': '비공개',
      'Public': '공개'
    },
    ar: {
      'Dashboard': 'لوحة التحكم',
      'Clubs': 'الأندية',
      'Events': 'الفعاليات',
      'Settings': 'الإعدادات',
      'Sign Out': 'تسجيل الخروج',
      'Log In': 'تسجيل الدخول',
      'Sign Up': 'إنشاء حساب',
      'Account Settings': 'إعدادات الحساب',
      'Manage your profile and preferences.': 'أدر ملفك الشخصي وتفضيلاتك.',
      'Profile': 'الملف الشخصي',
      'Profile Photo': 'صورة الملف الشخصي',
      'Choose image': 'اختر صورة',
      'Upload Photo': 'تحميل الصورة',
      'Username': 'اسم المستخدم',
      'Email Address': 'عنوان البريد الإلكتروني',
      'Phone Number': 'رقم الهاتف',
      'Update': 'تحديث',
      'Security': 'الأمان',
      'Change Password': 'تغيير كلمة المرور',
      'Current Password': 'كلمة المرور الحالية',
      'New Password': 'كلمة المرور الجديدة',
      'Confirm New Password': 'تأكيد كلمة المرور الجديدة',
      'Preferences': 'التفضيلات',
      'Display & Language': 'العرض واللغة',
      'Language': 'اللغة',
      'Theme': 'السمة',
      'Text Size': 'حجم النص',
      'Small': 'صغير',
      'Medium': 'متوسط',
      'Large': 'كبير',
      'Save Preferences': 'حفظ التفضيلات',
      'Account Info': 'معلومات الحساب',
      'Account ID': 'معرف الحساب',
      'Role': 'الدور',
      'Member Since': 'عضو منذ',
      'Student': 'طالب',
      'Administrator': 'مسؤول',
      'Campus Events': 'فعاليات الحرم الجامعي',
      "Discover what's happening around campus.": 'اكتشف ما يحدث في الحرم الجامعي.',
      'Create Event': 'إنشاء فعالية',
      'Create an Event': 'إنشاء فعالية',
      'Create a New Event': 'إنشاء فعالية جديدة',
      'Edit Event': 'تعديل الفعالية',
      'Event Title': 'عنوان الفعالية',
      'Date': 'التاريخ',
      'Time': 'الوقت',
      'Location': 'الموقع',
      'Google Maps Location': 'موقع خرائط Google',
      'Description': 'الوصف',
      'Capacity': 'السعة',
      'Hosting Club': 'النادي المستضيف',
      'Tags': 'الوسوم',
      'Visibility': 'الظهور',
      'Private event': 'فعالية خاصة',
      'Cancel': 'إلغاء',
      'Save Changes': 'حفظ التغييرات',
      'Details': 'التفاصيل',
      'RSVP': 'تأكيد الحضور',
      'RSVP to This Event': 'تأكيد الحضور لهذه الفعالية',
      'Cancel RSVP': 'إلغاء تأكيد الحضور',
      'Open in Google Maps': 'فتح في خرائط Google',
      'About This Event': 'حول هذه الفعالية',
      'Event Details': 'تفاصيل الفعالية',
      'Attendees': 'الحاضرون',
      'Organizer': 'المنظم',
      'Hosted by': 'يستضيفه',
      'Campus Clubs': 'أندية الحرم الجامعي',
      'Find your community.': 'اعثر على مجتمعك.',
      'Create Club': 'إنشاء نادي',
      'Join Club': 'الانضمام إلى النادي',
      'Leave Club': 'مغادرة النادي',
      'Club Events': 'فعاليات النادي',
      'Members': 'الأعضاء',
      'About': 'حول',
      'Private': 'خاص',
      'Public': 'عام'
    }
  };

  const dictionary = dictionaries[lang] || {};
  if (lang === 'ar') html.setAttribute('dir', 'rtl');

  const SKIP_TAGS = new Set(['SCRIPT', 'STYLE', 'TEXTAREA', 'NOSCRIPT']);
  const cacheKey = `campushub:i18n:${lang}`;
  const memoryCache = loadCache();

  function loadCache() {
    try {
      return JSON.parse(localStorage.getItem(cacheKey) || '{}');
    } catch (error) {
      return {};
    }
  }

  function saveCache() {
    try {
      localStorage.setItem(cacheKey, JSON.stringify(memoryCache));
    } catch (error) {
      // Cache failures should never block translation.
    }
  }

  function applyDictionary(text) {
    const trimmed = text.trim();
    if (!trimmed) return text;
    if (dictionary[trimmed]) return text.replace(trimmed, dictionary[trimmed]);

    let translated = trimmed;
    Object.keys(dictionary)
      .sort((a, b) => b.length - a.length)
      .forEach((key) => {
        translated = translated.replaceAll(key, dictionary[key]);
      });
    return translated === trimmed ? text : text.replace(trimmed, translated);
  }

  function shouldTranslateElement(element) {
    return element && !SKIP_TAGS.has(element.tagName) && !element.closest('[data-no-translate]');
  }

  async function googleTranslate(text) {
    const trimmed = text.trim();
    if (!trimmed || /^[\d\s#/:.,%-]+$/.test(trimmed)) return text;
    if (memoryCache[trimmed]) return text.replace(trimmed, memoryCache[trimmed]);

    const url = 'https://translate.googleapis.com/translate_a/single'
      + `?client=gtx&sl=auto&tl=${encodeURIComponent(lang)}&dt=t&q=${encodeURIComponent(trimmed)}`;

    const response = await fetch(url);
    if (!response.ok) throw new Error('Translation request failed.');
    const payload = await response.json();
    const translated = (payload[0] || []).map((part) => part[0]).join('').trim();
    if (!translated) return text;

    memoryCache[trimmed] = translated;
    saveCache();
    return text.replace(trimmed, translated);
  }

  function collectTextNodes() {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        return shouldTranslateElement(node.parentElement)
          ? NodeFilter.FILTER_ACCEPT
          : NodeFilter.FILTER_REJECT;
      }
    });

    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    return nodes;
  }

  function collectAttributes() {
    const attributes = [];
    document.querySelectorAll('[placeholder], [title], [aria-label], [alt], [value]').forEach((element) => {
      if (!shouldTranslateElement(element)) return;
      ['placeholder', 'title', 'aria-label', 'alt', 'value'].forEach((attribute) => {
        const value = element.getAttribute(attribute);
        if (!value) return;
        if (attribute === 'value' && !['BUTTON', 'INPUT'].includes(element.tagName)) return;
        if (attribute === 'value' && element.type && !['button', 'submit', 'reset'].includes(element.type)) return;
        attributes.push({ element, attribute, value });
      });
    });
    return attributes;
  }

  function translateWithDictionary(nodes) {
    nodes.forEach((node) => {
      node.nodeValue = applyDictionary(node.nodeValue);
    });
  }

  function translateAttributesWithDictionary(attributes) {
    attributes.forEach((item) => {
      const translated = applyDictionary(item.value);
      item.element.setAttribute(item.attribute, translated);
      item.value = translated;
    });
  }

  async function translateWithGoogle(nodes) {
    const candidates = nodes.filter((node) => {
      const text = node.nodeValue.trim();
      return text && !dictionary[text] && !/^[\d\s#/:.,%-]+$/.test(text);
    });

    for (const node of candidates) {
      try {
        node.nodeValue = await googleTranslate(node.nodeValue);
      } catch (error) {
        // Keep translated dictionary coverage even if the network fallback is blocked.
      }
    }
  }

  async function translateAttributesWithGoogle(attributes) {
    for (const item of attributes) {
      const text = item.value.trim();
      if (!text || dictionary[text] || /^[\d\s#/:.,%-]+$/.test(text)) continue;
      try {
        item.element.setAttribute(item.attribute, await googleTranslate(item.value));
      } catch (error) {
        // Attribute translation is best-effort when Google Translate is unavailable.
      }
    }
  }

  async function translatePage() {
    const nodes = collectTextNodes();
    const attributes = collectAttributes();

    translateWithDictionary(nodes);
    translateAttributesWithDictionary(attributes);

    await Promise.all([
      translateWithGoogle(nodes),
      translateAttributesWithGoogle(attributes)
    ]);
  }

  translatePage();
})();
