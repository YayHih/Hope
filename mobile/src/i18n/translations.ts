/**
 * Translations for Hope Platform
 * Supports: English (EN), Spanish (ES), Chinese (ZH)
 */

export type Language = 'EN' | 'ES' | 'ZH';

export interface Translations {
  // App header
  appTitle: string;

  // Navigation
  map: string;
  privacy: string;
  terms: string;
  report: string;
  providers: string;
  menu: string;
  closeMenu: string;
  about: string;
  howItWorks: string;
  reportAnIssue: string;
  providerPortal: string;
  language: string;

  // Map screen
  findingNearbyServices: string;
  showDHSResources: string;
  filters: string;
  closeFilters: string;
  time: string;
  openNow: string;
  categories: string;
  clearAllFilters: string;
  locationsFound: string;
  locationFound: string;
  viewDetails: string;
  kmAway: string;

  // DHS Info
  safeOptions: string;
  officialDHSResources: string;
  dhsPrivacyMessage: string;
  dhsContactMessage: string;
  call311: string;
  whatCanHelp: string;
  emergencyShelter: string;
  familyShelterIntake: string;
  singleAdultIntake: string;
  veteransServices: string;
  dhsFacilityInfo: string;
  backToMap: string;

  // Service categories
  food: string;
  shelter: string;
  medical: string;
  social: string;
  hygiene: string;

  // Report issue screen
  reportIssueTitle: string;
  reportIssueSubtitle: string;
  selectIssue: string;
  locationName: string;
  locationNamePlaceholder: string;
  briefExplanation: string;
  descriptionPlaceholder: string;
  submitReport: string;
  submitting: string;
  whatHappensNext: string;
  whatHappensNextText: string;
  forEmergencies: string;
  emergencyText: string;

  // Issue types
  locationClosed: string;
  hoursIncorrect: string;
  facilityFull: string;
  referralRequired: string;
  other: string;

  // Alerts and messages
  required: string;
  requiredField: string;
  pleaseSelectIssueType: string;
  pleaseEnterLocationName: string;
  pleaseProvideExplanation: string;
  noConnection: string;
  checkInternetConnection: string;
  thankYou: string;
  reportSubmitted: string;
  tooManyRequests: string;
  waitBeforeSubmitting: string;
  invalidRequest: string;
  checkInputTryAgain: string;
  error: string;
  unableToSubmitReport: string;
  couldNotLoadServices: string;

  // Offline
  noInternetConnection: string;
  someFeaturesUnavailable: string;
  youreOffline: string;
  featureRequiresInternet: string;
  tapToRetry: string;

  // Error boundary
  somethingWentWrong: string;
  unexpectedError: string;
  tryAgain: string;
  ifProblemPersists: string;
  closeReopenApp: string;
  checkInternet: string;
  updateToLatest: string;

  // Accessibility
  openMenu: string;
  opensNavigationMenu: string;
  english: string;
  spanish: string;
  chinese: string;
  switchToEnglish: string;
  switchToSpanish: string;
  switchToChinese: string;
  mapTab: string;
  findNearbyServices: string;
  privacyPolicyTab: string;
  termsOfUseTab: string;
  reportAnIssueTab: string;
  providerPortalTab: string;
}

export const translations: Record<Language, Translations> = {
  EN: {
    // App header
    appTitle: 'Hope for NYC',

    // Navigation
    map: 'Map',
    privacy: 'Privacy',
    terms: 'Terms',
    report: 'Report',
    providers: 'Providers',
    menu: 'Menu',
    closeMenu: 'Close menu',
    about: 'About',
    howItWorks: 'How This Works',
    reportAnIssue: 'Report an Issue',
    providerPortal: 'Provider Portal',
    language: 'Language',

    // Map screen
    findingNearbyServices: 'Finding nearby services...',
    showDHSResources: 'Show DHS / Official Resources',
    filters: 'Filters',
    closeFilters: 'Close Filters',
    time: 'Time',
    openNow: 'Open Now',
    categories: 'Categories',
    clearAllFilters: 'Clear All Filters',
    locationsFound: 'locations found',
    locationFound: 'location found',
    viewDetails: 'View Details',
    kmAway: 'km away',

    // DHS Info
    safeOptions: 'Safe Options',
    officialDHSResources: 'Official DHS Resources',
    dhsPrivacyMessage: 'For safety, confidential shelters are not listed on public maps.',
    dhsContactMessage: 'Please contact the Department of Homeless Services (DHS) or call 311 for placement.',
    call311: 'Call 311',
    whatCanHelp: 'What 311 Can Help With:',
    emergencyShelter: 'Emergency shelter placement',
    familyShelterIntake: 'Family shelter intake',
    singleAdultIntake: 'Single adult intake',
    veteransServices: 'Veterans services',
    dhsFacilityInfo: 'DHS facility information',
    backToMap: 'Back to Map',

    // Service categories
    food: 'Food',
    shelter: 'Shelter',
    medical: 'Medical',
    social: 'Social',
    hygiene: 'Hygiene',

    // Report issue screen
    reportIssueTitle: 'Report an Issue',
    reportIssueSubtitle: 'Help us keep our information accurate and up-to-date',
    selectIssue: 'Select Issue',
    locationName: 'Location Name',
    locationNamePlaceholder: "E.g., St. John's Bread & Life",
    briefExplanation: 'Brief Explanation',
    descriptionPlaceholder: 'Please describe the issue...',
    submitReport: 'Submit Report',
    submitting: 'Submitting...',
    whatHappensNext: 'What Happens Next?',
    whatHappensNextText: 'Our team will review your report and update the listing if necessary. This typically takes 1-3 business days.',
    forEmergencies: 'For Emergencies',
    emergencyText: "If you need immediate assistance or are in danger, please call 911 or contact NYC's 311 for service referrals.",

    // Issue types
    locationClosed: 'Location permanently closed',
    hoursIncorrect: 'Hours incorrect',
    facilityFull: 'Facility full/unavailable',
    referralRequired: 'Referral required',
    other: 'Other',

    // Alerts and messages
    required: '*',
    requiredField: 'Required Field',
    pleaseSelectIssueType: 'Please select an issue type.',
    pleaseEnterLocationName: 'Please enter the location name.',
    pleaseProvideExplanation: 'Please provide a brief explanation.',
    noConnection: 'No Connection',
    checkInternetConnection: 'Please check your internet connection and try again.',
    thankYou: 'Thank You!',
    reportSubmitted: 'Your report has been submitted. We will review it as soon as possible.',
    tooManyRequests: 'Too Many Requests',
    waitBeforeSubmitting: 'Please wait a moment before submitting another report.',
    invalidRequest: 'Invalid Request',
    checkInputTryAgain: 'Please check your input and try again.',
    error: 'Error',
    unableToSubmitReport: 'Unable to submit report. Please try again later.',
    couldNotLoadServices: 'Could not load nearby services. Please try again.',

    // Offline
    noInternetConnection: 'No Internet Connection',
    someFeaturesUnavailable: 'Some features may be unavailable',
    youreOffline: "You're Offline",
    featureRequiresInternet: 'This feature requires an internet connection',
    tapToRetry: 'Tap to Retry',

    // Error boundary
    somethingWentWrong: 'Something Went Wrong',
    unexpectedError: "We're sorry, but something unexpected happened. Please try again.",
    tryAgain: 'Try Again',
    ifProblemPersists: 'If this problem persists, please contact support or try:',
    closeReopenApp: 'Closing and reopening the app',
    checkInternet: 'Checking your internet connection',
    updateToLatest: 'Updating to the latest version',

    // Accessibility
    openMenu: 'Open menu',
    opensNavigationMenu: 'Opens the navigation menu',
    english: 'English',
    spanish: 'Spanish',
    chinese: 'Chinese',
    switchToEnglish: 'Switch to English language',
    switchToSpanish: 'Switch to Spanish language',
    switchToChinese: 'Switch to Chinese language',
    mapTab: 'Map tab',
    findNearbyServices: 'Find nearby services',
    privacyPolicyTab: 'Privacy policy tab',
    termsOfUseTab: 'Terms of use tab',
    reportAnIssueTab: 'Report an issue tab',
    providerPortalTab: 'Provider portal tab',
  },

  ES: {
    // App header
    appTitle: 'Esperanza para NYC',

    // Navigation
    map: 'Mapa',
    privacy: 'Privacidad',
    terms: 'Términos',
    report: 'Reportar',
    providers: 'Proveedores',
    menu: 'Menú',
    closeMenu: 'Cerrar menú',
    about: 'Acerca de',
    howItWorks: 'Cómo Funciona',
    reportAnIssue: 'Reportar un Problema',
    providerPortal: 'Portal de Proveedores',
    language: 'Idioma',

    // Map screen
    findingNearbyServices: 'Buscando servicios cercanos...',
    showDHSResources: 'Mostrar Recursos Oficiales de DHS',
    filters: 'Filtros',
    closeFilters: 'Cerrar Filtros',
    time: 'Hora',
    openNow: 'Abierto Ahora',
    categories: 'Categorías',
    clearAllFilters: 'Borrar Todos los Filtros',
    locationsFound: 'ubicaciones encontradas',
    locationFound: 'ubicación encontrada',
    viewDetails: 'Ver Detalles',
    kmAway: 'km de distancia',

    // DHS Info
    safeOptions: 'Opciones Seguras',
    officialDHSResources: 'Recursos Oficiales de DHS',
    dhsPrivacyMessage: 'Por seguridad, los refugios confidenciales no aparecen en mapas públicos.',
    dhsContactMessage: 'Por favor contacte al Departamento de Servicios para Personas sin Hogar (DHS) o llame al 311 para ubicación.',
    call311: 'Llamar al 311',
    whatCanHelp: 'En qué puede ayudar el 311:',
    emergencyShelter: 'Ubicación en refugio de emergencia',
    familyShelterIntake: 'Ingreso a refugio familiar',
    singleAdultIntake: 'Ingreso para adultos solteros',
    veteransServices: 'Servicios para veteranos',
    dhsFacilityInfo: 'Información de instalaciones DHS',
    backToMap: 'Volver al Mapa',

    // Service categories
    food: 'Comida',
    shelter: 'Refugio',
    medical: 'Médico',
    social: 'Social',
    hygiene: 'Higiene',

    // Report issue screen
    reportIssueTitle: 'Reportar un Problema',
    reportIssueSubtitle: 'Ayúdanos a mantener nuestra información precisa y actualizada',
    selectIssue: 'Seleccionar Problema',
    locationName: 'Nombre del Lugar',
    locationNamePlaceholder: 'Ej., St. John\'s Bread & Life',
    briefExplanation: 'Breve Explicación',
    descriptionPlaceholder: 'Por favor describa el problema...',
    submitReport: 'Enviar Reporte',
    submitting: 'Enviando...',
    whatHappensNext: '¿Qué Sigue?',
    whatHappensNextText: 'Nuestro equipo revisará su reporte y actualizará el listado si es necesario. Esto generalmente toma 1-3 días hábiles.',
    forEmergencies: 'Para Emergencias',
    emergencyText: 'Si necesita asistencia inmediata o está en peligro, por favor llame al 911 o contacte al 311 de NYC para referencias de servicios.',

    // Issue types
    locationClosed: 'Ubicación cerrada permanentemente',
    hoursIncorrect: 'Horario incorrecto',
    facilityFull: 'Instalación llena/no disponible',
    referralRequired: 'Se requiere referencia',
    other: 'Otro',

    // Alerts and messages
    required: '*',
    requiredField: 'Campo Requerido',
    pleaseSelectIssueType: 'Por favor seleccione un tipo de problema.',
    pleaseEnterLocationName: 'Por favor ingrese el nombre del lugar.',
    pleaseProvideExplanation: 'Por favor proporcione una breve explicación.',
    noConnection: 'Sin Conexión',
    checkInternetConnection: 'Por favor verifique su conexión a internet e intente de nuevo.',
    thankYou: '¡Gracias!',
    reportSubmitted: 'Su reporte ha sido enviado. Lo revisaremos lo antes posible.',
    tooManyRequests: 'Demasiadas Solicitudes',
    waitBeforeSubmitting: 'Por favor espere un momento antes de enviar otro reporte.',
    invalidRequest: 'Solicitud Inválida',
    checkInputTryAgain: 'Por favor verifique su información e intente de nuevo.',
    error: 'Error',
    unableToSubmitReport: 'No se pudo enviar el reporte. Por favor intente más tarde.',
    couldNotLoadServices: 'No se pudieron cargar los servicios cercanos. Por favor intente de nuevo.',

    // Offline
    noInternetConnection: 'Sin Conexión a Internet',
    someFeaturesUnavailable: 'Algunas funciones pueden no estar disponibles',
    youreOffline: 'Estás Desconectado',
    featureRequiresInternet: 'Esta función requiere conexión a internet',
    tapToRetry: 'Toca para Reintentar',

    // Error boundary
    somethingWentWrong: 'Algo Salió Mal',
    unexpectedError: 'Lo sentimos, pero algo inesperado ocurrió. Por favor intente de nuevo.',
    tryAgain: 'Intentar de Nuevo',
    ifProblemPersists: 'Si este problema persiste, por favor contacte soporte o intente:',
    closeReopenApp: 'Cerrar y reabrir la aplicación',
    checkInternet: 'Verificar su conexión a internet',
    updateToLatest: 'Actualizar a la última versión',

    // Accessibility
    openMenu: 'Abrir menú',
    opensNavigationMenu: 'Abre el menú de navegación',
    english: 'Inglés',
    spanish: 'Español',
    chinese: 'Chino',
    switchToEnglish: 'Cambiar a idioma inglés',
    switchToSpanish: 'Cambiar a idioma español',
    switchToChinese: 'Cambiar a idioma chino',
    mapTab: 'Pestaña de mapa',
    findNearbyServices: 'Encontrar servicios cercanos',
    privacyPolicyTab: 'Pestaña de política de privacidad',
    termsOfUseTab: 'Pestaña de términos de uso',
    reportAnIssueTab: 'Pestaña de reportar problema',
    providerPortalTab: 'Pestaña de portal de proveedores',
  },

  ZH: {
    // App header
    appTitle: '纽约希望',

    // Navigation
    map: '地图',
    privacy: '隐私',
    terms: '条款',
    report: '报告',
    providers: '服务商',
    menu: '菜单',
    closeMenu: '关闭菜单',
    about: '关于',
    howItWorks: '使用说明',
    reportAnIssue: '报告问题',
    providerPortal: '服务商门户',
    language: '语言',

    // Map screen
    findingNearbyServices: '正在搜索附近服务...',
    showDHSResources: '显示DHS/官方资源',
    filters: '筛选',
    closeFilters: '关闭筛选',
    time: '时间',
    openNow: '现在营业',
    categories: '类别',
    clearAllFilters: '清除所有筛选',
    locationsFound: '个地点',
    locationFound: '个地点',
    viewDetails: '查看详情',
    kmAway: '公里',

    // DHS Info
    safeOptions: '安全选择',
    officialDHSResources: '官方DHS资源',
    dhsPrivacyMessage: '为了安全起见，保密庇护所不会显示在公共地图上。',
    dhsContactMessage: '请联系无家可归者服务部（DHS）或拨打311获取安置服务。',
    call311: '拨打311',
    whatCanHelp: '311可以帮助您：',
    emergencyShelter: '紧急庇护所安置',
    familyShelterIntake: '家庭庇护所入住',
    singleAdultIntake: '单身成人入住',
    veteransServices: '退伍军人服务',
    dhsFacilityInfo: 'DHS设施信息',
    backToMap: '返回地图',

    // Service categories
    food: '食物',
    shelter: '庇护所',
    medical: '医疗',
    social: '社会服务',
    hygiene: '卫生',

    // Report issue screen
    reportIssueTitle: '报告问题',
    reportIssueSubtitle: '帮助我们保持信息准确和最新',
    selectIssue: '选择问题类型',
    locationName: '地点名称',
    locationNamePlaceholder: '例如：St. John\'s Bread & Life',
    briefExplanation: '简要说明',
    descriptionPlaceholder: '请描述问题...',
    submitReport: '提交报告',
    submitting: '正在提交...',
    whatHappensNext: '接下来会怎样？',
    whatHappensNextText: '我们的团队将审核您的报告，并在必要时更新列表。通常需要1-3个工作日。',
    forEmergencies: '紧急情况',
    emergencyText: '如果您需要紧急帮助或处于危险中，请拨打911或联系纽约市311获取服务转介。',

    // Issue types
    locationClosed: '地点已永久关闭',
    hoursIncorrect: '营业时间不正确',
    facilityFull: '设施已满/不可用',
    referralRequired: '需要转介',
    other: '其他',

    // Alerts and messages
    required: '*',
    requiredField: '必填项',
    pleaseSelectIssueType: '请选择问题类型。',
    pleaseEnterLocationName: '请输入地点名称。',
    pleaseProvideExplanation: '请提供简要说明。',
    noConnection: '无连接',
    checkInternetConnection: '请检查您的网络连接并重试。',
    thankYou: '谢谢！',
    reportSubmitted: '您的报告已提交。我们将尽快审核。',
    tooManyRequests: '请求过多',
    waitBeforeSubmitting: '请稍等片刻再提交另一份报告。',
    invalidRequest: '无效请求',
    checkInputTryAgain: '请检查您的输入并重试。',
    error: '错误',
    unableToSubmitReport: '无法提交报告。请稍后重试。',
    couldNotLoadServices: '无法加载附近服务。请重试。',

    // Offline
    noInternetConnection: '无网络连接',
    someFeaturesUnavailable: '部分功能可能不可用',
    youreOffline: '您已离线',
    featureRequiresInternet: '此功能需要网络连接',
    tapToRetry: '点击重试',

    // Error boundary
    somethingWentWrong: '出错了',
    unexpectedError: '抱歉，发生了意外错误。请重试。',
    tryAgain: '重试',
    ifProblemPersists: '如果问题持续存在，请联系支持或尝试：',
    closeReopenApp: '关闭并重新打开应用',
    checkInternet: '检查您的网络连接',
    updateToLatest: '更新到最新版本',

    // Accessibility
    openMenu: '打开菜单',
    opensNavigationMenu: '打开导航菜单',
    english: '英语',
    spanish: '西班牙语',
    chinese: '中文',
    switchToEnglish: '切换到英语',
    switchToSpanish: '切换到西班牙语',
    switchToChinese: '切换到中文',
    mapTab: '地图标签',
    findNearbyServices: '查找附近服务',
    privacyPolicyTab: '隐私政策标签',
    termsOfUseTab: '使用条款标签',
    reportAnIssueTab: '报告问题标签',
    providerPortalTab: '服务商门户标签',
  },
};
