import { useEffect, useState } from 'react';
import { SmartCaptcha } from '@yandex/smart-captcha';
import { authAPI } from '../../api/auth';

const CaptchaWidget = ({ onVerify, resetTrigger }) => {
  const [siteKey, setSiteKey] = useState('');
  const [captchaKey, setCaptchaKey] = useState(0);

  useEffect(() => {
    authAPI.getCaptchaConfig()
      .then(res => setSiteKey(res.data.site_key))
      .catch(err => console.error('Failed to load captcha config', err));
  }, []);

  useEffect(() => {
    if (resetTrigger > 0) {
      setCaptchaKey(prev => prev + 1);
    }
  }, [resetTrigger]);

  const handleSuccess = (token) => {
    onVerify(token);
  };

  if (!siteKey) return <div>Загрузка капчи...</div>;

  return (
    <SmartCaptcha
      key={captchaKey}
      sitekey={siteKey}
      onSuccess={handleSuccess}
      language="ru"
    />
  );
};

export default CaptchaWidget;