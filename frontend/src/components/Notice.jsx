import { AlertIcon, CheckIcon, InfoIcon } from './Icons.jsx';

// A coloured box with an icon: tone = info | warn | error | good.
export default function Notice({ tone = 'info', title, children, actions, live = false }) {
  const Icon = tone === 'good' ? CheckIcon : tone === 'info' ? InfoIcon : AlertIcon;
  return (
    <div className="notice" data-tone={tone} role={live ? (tone === 'error' ? 'alert' : 'status') : undefined}>
      <Icon className="notice-icon" />
      <div className="notice-body">
        {title && <p className="notice-title">{title}</p>}
        {children && <div className="notice-text">{children}</div>}
        {actions && <div className="notice-actions">{actions}</div>}
      </div>
    </div>
  );
}
