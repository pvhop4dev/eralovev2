"use client";

import { useState, useEffect, useMemo } from "react";
import { Button } from "@/components/atoms/button";
import { FormField } from "@/components/molecules/form-field";

const EVENT_TYPES = [
  { id: "date", icon: "❤️", label: "Hẹn hò" },
  { id: "anniversary", icon: "💍", label: "Kỷ niệm" },
  { id: "travel", icon: "✈️", label: "Du lịch" },
  { id: "birthday", icon: "🎂", label: "Sinh nhật" },
  { id: "custom", icon: "⭐", label: "Khác" },
];

const DAYS = ["CN", "T2", "T3", "T4", "T5", "T6", "T7"];
const MONTHS = [
  "Tháng 1", "Tháng 2", "Tháng 3", "Tháng 4", "Tháng 5", "Tháng 6",
  "Tháng 7", "Tháng 8", "Tháng 9", "Tháng 10", "Tháng 11", "Tháng 12",
];

export default function CalendarPage() {
  const today = new Date();
  const [currentYear, setCurrentYear] = useState(today.getFullYear());
  const [currentMonth, setCurrentMonth] = useState(today.getMonth()); // 0-indexed
  const [events, setEvents] = useState<any[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    event_type: "date",
    event_date: "",
    event_time: "",
    description: "",
    location_name: "",
  });

  useEffect(() => {
    fetchEvents();
  }, [currentYear, currentMonth]);

  const fetchEvents = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/events?year=${currentYear}&month=${currentMonth + 1}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
        }
      );
      if (res.ok) {
        const data = await res.json();
        setEvents(data.data?.events || []);
      }
    } catch {}
  };

  const handleCreateEvent = async () => {
    if (!formData.title || !formData.event_date) return;
    setIsLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/events`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
          },
          body: JSON.stringify({
            title: formData.title,
            event_type: formData.event_type,
            event_date: formData.event_date,
            event_time: formData.event_time || undefined,
            description: formData.description || undefined,
            location_name: formData.location_name || undefined,
          }),
        }
      );
      if (res.ok) {
        setShowCreate(false);
        setFormData({ title: "", event_type: "date", event_date: "", event_time: "", description: "", location_name: "" });
        fetchEvents();
      }
    } catch {} finally {
      setIsLoading(false);
    }
  };

  // Calendar grid
  const calendarDays = useMemo(() => {
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    const days: (number | null)[] = [];
    for (let i = 0; i < firstDay; i++) days.push(null);
    for (let i = 1; i <= daysInMonth; i++) days.push(i);
    return days;
  }, [currentYear, currentMonth]);

  const getEventsForDay = (day: number) => {
    const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    return events.filter((e) => e.event_date === dateStr);
  };

  const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

  const prevMonth = () => {
    if (currentMonth === 0) { setCurrentMonth(11); setCurrentYear(currentYear - 1); }
    else setCurrentMonth(currentMonth - 1);
  };
  const nextMonth = () => {
    if (currentMonth === 11) { setCurrentMonth(0); setCurrentYear(currentYear + 1); }
    else setCurrentMonth(currentMonth + 1);
  };

  const selectedEvents = selectedDate ? events.filter((e) => e.event_date === selectedDate) : [];

  return (
    <div style={{ padding: "1.5rem", maxWidth: "800px", margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h1 style={{ fontFamily: "var(--font-heading)", fontSize: "1.5rem", fontWeight: 700 }}>
          📅 Lịch Yêu Thương
        </h1>
        <Button size="sm" onClick={() => setShowCreate(true)}>+ Sự kiện</Button>
      </div>

      {/* Month nav */}
      <div
        style={{
          background: "var(--card)",
          borderRadius: "var(--radius-xl)",
          padding: "1.5rem",
          boxShadow: "var(--shadow-card)",
          border: "1px solid var(--border)",
          marginBottom: "1rem",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <button onClick={prevMonth} style={{ background: "none", border: "none", cursor: "pointer", fontSize: "1.25rem", color: "var(--muted-foreground)" }}>
            ←
          </button>
          <span style={{ fontWeight: 700, fontSize: "1rem" }}>
            {MONTHS[currentMonth]} {currentYear}
          </span>
          <button onClick={nextMonth} style={{ background: "none", border: "none", cursor: "pointer", fontSize: "1.25rem", color: "var(--muted-foreground)" }}>
            →
          </button>
        </div>

        {/* Day headers */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: "2px", marginBottom: "0.5rem" }}>
          {DAYS.map((d) => (
            <div key={d} style={{ textAlign: "center", fontSize: "0.7rem", fontWeight: 600, color: "var(--muted-foreground)", padding: "0.25rem" }}>
              {d}
            </div>
          ))}
        </div>

        {/* Calendar grid */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: "2px" }}>
          {calendarDays.map((day, i) => {
            if (day === null) return <div key={`empty-${i}`} />;
            const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
            const dayEvents = getEventsForDay(day);
            const isToday = dateStr === todayStr;
            const isSelected = dateStr === selectedDate;

            return (
              <button
                key={day}
                type="button"
                onClick={() => setSelectedDate(dateStr)}
                style={{
                  position: "relative",
                  padding: "0.5rem 0.25rem",
                  textAlign: "center",
                  borderRadius: "var(--radius-sm)",
                  border: "none",
                  cursor: "pointer",
                  background: isSelected
                    ? "var(--gradient-primary)"
                    : isToday
                    ? "rgba(255,107,157,0.15)"
                    : "transparent",
                  color: isSelected ? "white" : "var(--foreground)",
                  fontWeight: isToday || isSelected ? 700 : 400,
                  fontSize: "0.85rem",
                  transition: "all 0.15s ease",
                  minHeight: "40px",
                }}
              >
                {day}
                {dayEvents.length > 0 && (
                  <div style={{ display: "flex", justifyContent: "center", gap: "1px", marginTop: "2px" }}>
                    {dayEvents.slice(0, 3).map((e, j) => (
                      <span key={j} style={{ fontSize: "0.5rem" }}>{e.icon}</span>
                    ))}
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected day events */}
      {selectedDate && (
        <div
          style={{
            background: "var(--card)",
            borderRadius: "var(--radius-xl)",
            padding: "1.25rem",
            boxShadow: "var(--shadow-card)",
            border: "1px solid var(--border)",
            marginBottom: "1rem",
          }}
        >
          <h3 style={{ fontSize: "0.9rem", fontWeight: 600, marginBottom: "0.75rem" }}>
            📌 {selectedDate}
          </h3>
          {selectedEvents.length === 0 ? (
            <p style={{ color: "var(--muted-foreground)", fontSize: "0.85rem" }}>
              Không có sự kiện nào.{" "}
              <button
                type="button"
                onClick={() => { setFormData({ ...formData, event_date: selectedDate }); setShowCreate(true); }}
                style={{ color: "var(--color-rose-petal)", fontWeight: 600, background: "none", border: "none", cursor: "pointer" }}
              >
                Thêm mới?
              </button>
            </p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {selectedEvents.map((e) => (
                <div
                  key={e.id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.75rem",
                    padding: "0.75rem",
                    borderRadius: "var(--radius-md)",
                    background: "rgba(255,107,157,0.05)",
                    border: "1px solid var(--border)",
                  }}
                >
                  <span style={{ fontSize: "1.25rem" }}>{e.icon}</span>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: "0.875rem" }}>{e.title}</div>
                    {e.location_name && (
                      <div style={{ fontSize: "0.75rem", color: "var(--muted-foreground)" }}>📍 {e.location_name}</div>
                    )}
                  </div>
                  {e.event_time && (
                    <span style={{ fontSize: "0.75rem", color: "var(--muted-foreground)" }}>🕐 {e.event_time}</span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Create event modal */}
      {showCreate && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
            padding: "1rem",
          }}
          onClick={(e) => e.target === e.currentTarget && setShowCreate(false)}
        >
          <div
            style={{
              background: "var(--card)",
              borderRadius: "var(--radius-xl)",
              padding: "1.5rem",
              width: "100%",
              maxWidth: "440px",
              maxHeight: "80vh",
              overflow: "auto",
            }}
          >
            <h2 style={{ fontFamily: "var(--font-heading)", fontSize: "1.25rem", fontWeight: 700, marginBottom: "1.25rem" }}>
              ✨ Tạo sự kiện mới
            </h2>

            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <FormField
                label="Tên sự kiện"
                name="title"
                type="text"
                placeholder="Valentine's Day 💕"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />

              {/* Event type selector */}
              <div>
                <label style={{ fontSize: "0.85rem", fontWeight: 500, display: "block", marginBottom: "0.5rem" }}>
                  Loại sự kiện
                </label>
                <div style={{ display: "flex", gap: "0.375rem", flexWrap: "wrap" }}>
                  {EVENT_TYPES.map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setFormData({ ...formData, event_type: t.id })}
                      style={{
                        padding: "0.5rem 0.75rem",
                        borderRadius: "9999px",
                        border: `2px solid ${formData.event_type === t.id ? "var(--color-rose-petal)" : "var(--border)"}`,
                        background: formData.event_type === t.id ? "rgba(255,107,157,0.1)" : "transparent",
                        cursor: "pointer",
                        fontSize: "0.8rem",
                        fontWeight: formData.event_type === t.id ? 600 : 400,
                        color: "var(--foreground)",
                      }}
                    >
                      {t.icon} {t.label}
                    </button>
                  ))}
                </div>
              </div>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
                <FormField
                  label="Ngày"
                  name="event_date"
                  type="date"
                  value={formData.event_date}
                  onChange={(e) => setFormData({ ...formData, event_date: e.target.value })}
                  required
                />
                <FormField
                  label="Giờ"
                  name="event_time"
                  type="time"
                  value={formData.event_time}
                  onChange={(e) => setFormData({ ...formData, event_time: e.target.value })}
                />
              </div>

              <FormField
                label="Địa điểm"
                name="location_name"
                type="text"
                placeholder="Hồ Gươm, Hà Nội"
                value={formData.location_name}
                onChange={(e) => setFormData({ ...formData, location_name: e.target.value })}
              />

              <div style={{ display: "flex", gap: "0.75rem", marginTop: "0.5rem" }}>
                <Button variant="ghost" onClick={() => setShowCreate(false)} style={{ flex: 1 }}>
                  Hủy
                </Button>
                <Button onClick={handleCreateEvent} isLoading={isLoading} style={{ flex: 2 }}>
                  Tạo sự kiện 🎉
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
