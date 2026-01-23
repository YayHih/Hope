import React, { useState } from 'react';
import { OperatingHours, formatTime, getTodayDayOfWeek } from './mapHelpers';

interface WeeklyHoursDropdownProps {
  hours: OperatingHours[];
  t: (key: any) => string;
  isDark: boolean;
}

export const WeeklyHoursDropdown: React.FC<WeeklyHoursDropdownProps> = ({ hours, t, isDark }) => {
  const [isOpen, setIsOpen] = useState(false);

  const dayKeys = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'] as const;

  const hoursGroupedByDay = dayKeys.map((dayKey, dayIndex) => {
    const dayHours = hours.filter(h => h.day_of_week === dayIndex);
    const primaryHours = dayHours[0];

    if (!primaryHours) {
      return { day: t(dayKey), text: t('hoursNotAvailable') };
    }

    let hoursText = '';
    if (primaryHours.is_closed) {
      hoursText = t('closed');
    } else if (primaryHours.is_24_hours) {
      hoursText = t('hours24');
      if (primaryHours.notes) hoursText += ` (${primaryHours.notes})`;
    } else if (primaryHours.open_time && primaryHours.close_time) {
      const openTime = formatTime(primaryHours.open_time);
      const closeTime = formatTime(primaryHours.close_time);
      hoursText = `${openTime} - ${closeTime}`;
      if (primaryHours.notes) hoursText += ` (${primaryHours.notes})`;
    } else if (primaryHours.notes) {
      hoursText = primaryHours.notes;
    } else {
      hoursText = t('hoursNotAvailable');
    }

    return { day: t(dayKey), text: hoursText };
  });

  const today = getTodayDayOfWeek();

  const bgColor = isDark ? '#374151' : '#f8f9fa';
  const borderColor = isDark ? '#4B5563' : '#dee2e6';
  const textColor = isDark ? '#F3F4F6' : '#333';
  const todayBgColor = isDark ? '#92400E' : '#fff3cd';

  return (
    <div style={{ marginTop: '8px' }}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        style={{
          backgroundColor: bgColor,
          border: `1px solid ${borderColor}`,
          borderRadius: '4px',
          padding: '4px 8px',
          fontSize: '0.8em',
          cursor: 'pointer',
          width: '100%',
          textAlign: 'left',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          color: textColor,
        }}
      >
        <span>📅 {t('viewAllHours')}</span>
        <span>{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div style={{
          marginTop: '4px',
          padding: '6px',
          backgroundColor: bgColor,
          borderRadius: '4px',
          fontSize: '0.8em',
          color: textColor,
        }}>
          {hoursGroupedByDay.map((item, idx) => (
            <div
              key={idx}
              style={{
                padding: '4px 0',
                borderBottom: idx < hoursGroupedByDay.length - 1 ? `1px solid ${borderColor}` : 'none',
                fontWeight: idx === today ? 'bold' : 'normal',
                backgroundColor: idx === today ? todayBgColor : 'transparent',
                paddingLeft: idx === today ? '4px' : '0',
                borderRadius: '2px'
              }}
            >
              <strong>{item.day}:</strong> {item.text}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
