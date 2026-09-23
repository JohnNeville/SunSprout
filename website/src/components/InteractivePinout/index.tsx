import React, { useState, useEffect, useRef, useMemo } from 'react';
import useBaseUrl from '@docusaurus/useBaseUrl';
import clsx from 'clsx';
import styles from './styles.module.css';

export interface InteractivePinoutProps {
  board: 'hub' | 'satellite';
  src?: string;
  topSrc?: string;
  bottomSrc?: string;
  title?: string;
}

interface FilterOption {
  id: string;
  label: string;
  tags: string[];
}

const HUB_FILTERS: FilterOption[] = [
  { id: 'all', label: 'All Signals', tags: [] },
  { id: 'pwr', label: 'Power & GND', tags: ['pwr', 'gnd'] },
  { id: 'gpio', label: 'Free GPIOs', tags: ['gpio', 'lp-gpio'] },
  { id: 'i2c', label: 'I2C Buses', tags: ['i2c-user', 'i2c-int', 'diff'] },
  { id: 'uart', label: 'UART Console', tags: ['uart'] },
  { id: 'strap', label: 'Strapping Pins', tags: ['strap'] },
  { id: 'btn', label: 'Buttons', tags: ['btn'] },
  { id: 'usb', label: 'USB-C', tags: ['usb'] },
];

const HUB_BOTTOM_FILTERS: FilterOption[] = [
  { id: 'all', label: 'All Test Points', tags: [] },
  { id: 'pwr', label: 'Power & GND', tags: ['pwr', 'gnd'] },
  { id: 'uart', label: 'UART Console', tags: ['uart'] },
  { id: 'i2c', label: 'Internal I2C', tags: ['i2c-int'] },
  { id: 'ctrl', label: 'Control & Boot', tags: ['strap', 'btn'] },
  { id: 'jumper', label: 'Jumpers', tags: ['jumper'] },
];

const SATELLITE_TOP_FILTERS: FilterOption[] = [
  { id: 'all', label: 'All Signals', tags: [] },
  { id: 'sensor', label: 'Sensor Inputs', tags: ['analog', 'onewire', 'sensor'] },
  { id: 'diff', label: 'Differential & Bus', tags: ['diff', 'i2c-user'] },
  { id: 'pwr', label: 'Power & GND', tags: ['pwr', 'gnd'] },
  { id: 'jumper', label: 'Jumpers & Cuts', tags: ['jumper', 'strap'] },
];

const SATELLITE_BOTTOM_FILTERS: FilterOption[] = [
  { id: 'all', label: 'All Jumpers', tags: [] },
  { id: 'addr', label: 'Address Jumpers', tags: ['addr'] },
  { id: 'pwr', label: 'Power Routing', tags: ['pwr'] },
  { id: 'gnd', label: 'Ground & Shield', tags: ['gnd'] },
];

export default function InteractivePinout({
  board,
  src,
  topSrc,
  bottomSrc,
}: InteractivePinoutProps): React.JSX.Element {
  const [activeSide, setActiveSide] = useState<'top' | 'bottom'>('top');
  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [isFullscreen, setIsFullscreen] = useState<boolean>(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [hoveredInfo, setHoveredInfo] = useState<string | null>(null);
  const [svgContent, setSvgContent] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(true);

  const containerRef = useRef<HTMLDivElement>(null);
  const svgWrapperRef = useRef<HTMLDivElement>(null);

  // Fullscreen change listener
  useEffect(() => {
    const handleFullscreenChange = () => {
      const isCurrentFs = document.fullscreenElement === containerRef.current;
      setIsFullscreen(isCurrentFs);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    document.addEventListener('webkitfullscreenchange', handleFullscreenChange);

    return () => {
      document.removeEventListener('fullscreenchange', handleFullscreenChange);
      document.removeEventListener('webkitfullscreenchange', handleFullscreenChange);
    };
  }, []);

  // Escape key handler for CSS fullscreen fallback
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isFullscreen) {
        if (document.fullscreenElement) {
          document.exitFullscreen().catch(() => {});
        } else {
          setIsFullscreen(false);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFullscreen]);

  // Lock body scroll when in fullscreen
  useEffect(() => {
    if (isFullscreen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isFullscreen]);

  const toggleFullscreen = async () => {
    if (!containerRef.current) return;

    if (!document.fullscreenElement && !isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        try {
          await containerRef.current.requestFullscreen();
        } catch {
          setIsFullscreen(true);
        }
      } else {
        setIsFullscreen(true);
      }
    } else {
      if (document.fullscreenElement) {
        try {
          await document.exitFullscreen();
        } catch {
          setIsFullscreen(false);
        }
      } else {
        setIsFullscreen(false);
      }
    }
  };

  // Resolve current SVG URL based on side / props
  const rawUrl = useMemo(() => {
    return activeSide === 'bottom' ? (bottomSrc || src) : (topSrc || src);
  }, [activeSide, src, topSrc, bottomSrc]);

  const targetUrl = useBaseUrl(rawUrl || '');

  // Select appropriate filter list
  const filterList = useMemo(() => {
    if (board === 'satellite') {
      return activeSide === 'bottom' ? SATELLITE_BOTTOM_FILTERS : SATELLITE_TOP_FILTERS;
    }
    return activeSide === 'bottom' ? HUB_BOTTOM_FILTERS : HUB_FILTERS;
  }, [board, activeSide]);

  // Fetch SVG text when URL changes
  useEffect(() => {
    if (!targetUrl) return;
    setIsLoading(true);
    let isCancelled = false;

    fetch(targetUrl)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP error ${res.status}`);
        return res.text();
      })
      .then((text) => {
        if (!isCancelled) {
          setSvgContent(text);
          setIsLoading(false);
          setActiveFilter('all');
        }
      })
      .catch((err) => {
        console.error('Failed to load pinout SVG:', err);
        if (!isCancelled) {
          setIsLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [targetUrl]);

  // Update SVG DOM elements when filter or SVG content changes
  useEffect(() => {
    if (!svgWrapperRef.current) return;
    const svgEl = svgWrapperRef.current.querySelector('svg');
    if (!svgEl) return;

    const calloutGroups = svgEl.querySelectorAll('.callout-group');
    if (!calloutGroups.length) return;

    const selectedOption = filterList.find((f) => f.id === activeFilter);
    const activeTags = selectedOption?.tags || [];

    calloutGroups.forEach((group) => {
      const g = group as SVGElement;
      if (activeFilter === 'all' || activeTags.length === 0) {
        g.classList.remove('is-dimmed');
        g.classList.remove('is-highlighted');
      } else {
        const itemTags = (g.getAttribute('data-tags') || '').split(',').map((t) => t.trim());
        const hasMatch = activeTags.some((t) => itemTags.includes(t));
        if (hasMatch) {
          g.classList.add('is-highlighted');
          g.classList.remove('is-dimmed');
        } else {
          g.classList.add('is-dimmed');
          g.classList.remove('is-highlighted');
        }
      }
    });
  }, [svgContent, activeFilter, filterList]);

  // Attach event listeners for click-to-copy, hover tooltip, and legend clicking
  useEffect(() => {
    if (!svgWrapperRef.current) return;
    const svgEl = svgWrapperRef.current.querySelector('svg');
    if (!svgEl) return;

    const handleMouseMove = (e: MouseEvent) => {
      const target = e.target as Element | null;
      const callout = target?.closest('.callout-group');
      if (callout) {
        const name = callout.getAttribute('data-name');
        const pin = callout.getAttribute('data-pin');
        setHoveredInfo(pin ? `${pin}: ${name}` : name);
      } else {
        setHoveredInfo(null);
      }
    };

    const handleMouseLeave = () => {
      setHoveredInfo(null);
    };

    const handleClick = (e: MouseEvent) => {
      const target = e.target as Element | null;

      // Check for callout click (copy to clipboard)
      const callout = target?.closest('.callout-group');
      if (callout) {
        const pin = callout.getAttribute('data-pin');
        const name = callout.getAttribute('data-name');
        const textToCopy = pin || name;
        if (textToCopy && navigator.clipboard) {
          navigator.clipboard.writeText(textToCopy).then(() => {
            setToastMessage(`Copied "${textToCopy}" to clipboard`);
            setTimeout(() => setToastMessage(null), 2200);
          });
        }
        return;
      }

      // Check for legend badge click (filter by tag)
      const legendBadge = target?.closest('.legend-badge');
      if (legendBadge) {
        const tag = legendBadge.getAttribute('data-tag');
        if (tag) {
          const matchedFilter = filterList.find((f) => f.tags.includes(tag));
          if (matchedFilter) {
            setActiveFilter((prev) => (prev === matchedFilter.id ? 'all' : matchedFilter.id));
          }
        }
      }
    };

    svgEl.addEventListener('mousemove', handleMouseMove);
    svgEl.addEventListener('mouseleave', handleMouseLeave);
    svgEl.addEventListener('click', handleClick);

    return () => {
      svgEl.removeEventListener('mousemove', handleMouseMove);
      svgEl.removeEventListener('mouseleave', handleMouseLeave);
      svgEl.removeEventListener('click', handleClick);
    };
  }, [svgContent, filterList]);

  return (
    <div
      className={clsx(styles.container, isFullscreen && styles.containerFullscreen)}
      ref={containerRef}
    >
      <div className={styles.toolbar}>
        <div className={styles.filterGroup}>
          <span className={styles.filterLabel}>Filter:</span>
          {filterList.map((f) => (
            <button
              key={f.id}
              type="button"
              className={clsx(styles.filterChip, activeFilter === f.id && styles.filterChipActive)}
              onClick={() => setActiveFilter((prev) => (prev === f.id ? 'all' : f.id))}
            >
              {f.label}
            </button>
          ))}
        </div>

        <div className={styles.toolbarActions}>
          {bottomSrc && (
            <div className={styles.viewToggle}>
              <button
                type="button"
                className={clsx(styles.viewButton, activeSide === 'top' && styles.viewButtonActive)}
                onClick={() => setActiveSide('top')}
              >
                {board === 'satellite' ? 'Top (Ports)' : 'Top (Signals)'}
              </button>
              <button
                type="button"
                className={clsx(styles.viewButton, activeSide === 'bottom' && styles.viewButtonActive)}
                onClick={() => setActiveSide('bottom')}
              >
                {board === 'satellite' ? 'Bottom (Jumpers)' : 'Bottom (Test Points)'}
              </button>
            </div>
          )}

          <button
            type="button"
            className={clsx(styles.fullscreenButton, isFullscreen && styles.fullscreenButtonActive)}
            onClick={toggleFullscreen}
            title={isFullscreen ? 'Exit Fullscreen (Esc)' : 'Enter Fullscreen'}
            aria-label={isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
          >
            {isFullscreen ? (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M8 3v3a2 2 0 0 1-2 2H3m18 0h-3a2 2 0 0 1-2-2V3m0 18v-3a2 2 0 0 1 2-2h3M3 16h3a2 2 0 0 1 2 2v3" />
              </svg>
            ) : (
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3" />
              </svg>
            )}
            <span>{isFullscreen ? 'Exit Fullscreen' : 'Fullscreen'}</span>
          </button>
        </div>
      </div>

      <div className={styles.hintBar}>
        {hoveredInfo ? (
          <span className={styles.inspectedPin}>
            <span className={styles.inspectDot} />
            Inspecting: <strong>{hoveredInfo}</strong> — <em>click to copy</em>
          </span>
        ) : (
          <span>Hover over any pin to inspect • Click to copy identifier</span>
        )}

        {activeFilter !== 'all' && (
          <span className={styles.activeFilterTag}>
            Filter: {filterList.find((f) => f.id === activeFilter)?.label}
          </span>
        )}
      </div>

      <div className={styles.svgWrapper}>
        {isLoading ? (
          <div className={styles.loading}>Loading interactive vector diagram...</div>
        ) : (
          <div
            ref={svgWrapperRef}
            className={styles.svgInner}
            dangerouslySetInnerHTML={{ __html: svgContent }}
          />
        )}

        {toastMessage && <div className={styles.toast}>{toastMessage}</div>}
      </div>
    </div>
  );
}
