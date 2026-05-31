"use client";

import { useState, useEffect, useMemo, useRef } from "react";
import { Button } from "@/components/atoms/button";
import { FormField } from "@/components/molecules/form-field";
import { toast } from "sonner";

interface EventPhoto {
  id: string;
  original_url: string;
  caption: string | null;
  photo_date: string | null;
}

interface LoveEvent {
  id: string;
  couple_id: string;
  created_by: string;
  title: string;
  description: string | null;
  event_type: string;
  event_date: string;
  event_time: string | null;
  end_date: string | null;
  location_name: string | null;
  icon: string;
  color: string | null;
  is_recurring: boolean;
}

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
  const [events, setEvents] = useState<LoveEvent[]>([]);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  
  // Modals state
  const [showCreate, setShowCreate] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [showDayDetail, setShowDayDetail] = useState(false);
  
  const [isLoading, setIsLoading] = useState(false);
  const [photosByEvent, setPhotosByEvent] = useState<Record<string, EventPhoto[]>>({});
  const [isUploading, setIsUploading] = useState<string | null>(null); // maps to eventId
  const fileInputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  const [formData, setFormData] = useState({
    title: "",
    event_type: "date",
    event_date: "",
    event_time: "",
    description: "",
    location_name: "",
  });

  const [editFormData, setEditFormData] = useState({
    id: "",
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

  const getHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
  });

  const fetchEvents = async () => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/events?year=${currentYear}&month=${currentMonth + 1}`,
        { headers: getHeaders() }
      );
      if (res.ok) {
        const data = await res.json();
        setEvents(data.data?.events || []);
      }
    } catch {
      toast.error("Không thể tải danh sách sự kiện");
    }
  };

  const fetchPhotosForEvent = async (eventId: string) => {
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/photos/event/${eventId}`,
        { headers: getHeaders() }
      );
      if (res.ok) {
        const data = await res.json();
        setPhotosByEvent((prev) => ({
          ...prev,
          [eventId]: data.data?.photos || [],
        }));
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
            ...getHeaders(),
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
        toast.success("Tạo sự kiện thành công! 🎉");
        setShowCreate(false);
        setFormData({ title: "", event_type: "date", event_date: "", event_time: "", description: "", location_name: "" });
        fetchEvents();
        if (selectedDate === formData.event_date) {
          // Refresh details if open
          setSelectedDate(formData.event_date);
        }
      } else {
        const data = await res.json();
        toast.error(data.error?.message || "Lỗi tạo sự kiện");
      }
    } catch {
      toast.error("Lỗi kết nối đến máy chủ");
    } finally {
      setIsLoading(false);
    }
  };

  const handleEditEvent = async () => {
    if (!editFormData.title || !editFormData.event_date) return;
    setIsLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/events/${editFormData.id}`,
        {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            ...getHeaders(),
          },
          body: JSON.stringify({
            title: editFormData.title,
            event_type: editFormData.event_type,
            event_date: editFormData.event_date,
            event_time: editFormData.event_time || undefined,
            description: editFormData.description || undefined,
            location_name: editFormData.location_name || undefined,
          }),
        }
      );
      if (res.ok) {
        toast.success("Cập nhật sự kiện thành công! ✏️");
        setShowEdit(false);
        fetchEvents();
      } else {
        const data = await res.json();
        toast.error(data.error?.message || "Lỗi cập nhật sự kiện");
      }
    } catch {
      toast.error("Lỗi kết nối đến máy chủ");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteEvent = async (eventId: string) => {
    if (!confirm("Bạn có chắc chắn muốn xóa sự kiện này không?")) return;
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/events/${eventId}`,
        {
          method: "DELETE",
          headers: getHeaders(),
        }
      );
      if (res.ok) {
        toast.success("Xóa sự kiện thành công! 🗑️");
        fetchEvents();
        // If no events left on that day, we could auto-close day details
        const updatedSelectedEvents = events.filter((e) => e.id !== eventId && e.event_date === selectedDate);
        if (updatedSelectedEvents.length === 0) {
          setShowDayDetail(false);
        }
      } else {
        const data = await res.json();
        toast.error(data.error?.message || "Lỗi xóa sự kiện");
      }
    } catch {
      toast.error("Lỗi kết nối đến máy chủ");
    }
  };

  // Photo uploading flow
  const handleFileChange = async (eventId: string, eventDate: string, fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    const file = fileList[0];
    
    setIsUploading(eventId);
    try {
      // 1. Get presigned upload URL
      const presignedRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/storage/presigned-url`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...getHeaders(),
          },
          body: JSON.stringify({
            file_name: file.name,
            content_type: file.type,
            file_type: "event",
          }),
        }
      );

      if (!presignedRes.ok) {
        throw new Error("Không thể tạo link tải ảnh lên");
      }

      const presignedData = await presignedRes.json();
      const { upload_url, file_url } = presignedData.data;

      // 2. Put file to S3/MinIO
      const uploadRes = await fetch(upload_url, {
        method: "PUT",
        headers: {
          "Content-Type": file.type,
        },
        body: file,
      });

      if (!uploadRes.ok) {
        throw new Error("Lỗi tải ảnh lên S3/MinIO");
      }

      // 3. Extract s3 key (format: events/{uuid}.jpg)
      const match = file_url.match(/(events\/[^?#]+)/);
      const s3Key = match ? match[1] : "";

      // 4. Save metadata to API
      const saveRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/photos`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...getHeaders(),
          },
          body: JSON.stringify({
            s3_key: s3Key,
            original_url: file_url,
            event_id: eventId,
            caption: file.name.split(".")[0], // default caption as filename
            photo_date: eventDate,
          }),
        }
      );

      if (saveRes.ok) {
        toast.success("Tải kỷ niệm lên thành công! 📸");
        fetchPhotosForEvent(eventId);
      } else {
        throw new Error("Không thể lưu thông tin ảnh");
      }
    } catch (err: any) {
      toast.error(err.message || "Đã xảy ra lỗi khi tải ảnh lên");
    } finally {
      setIsUploading(null);
    }
  };

  const handleDeletePhoto = async (photoId: string, eventId: string) => {
    if (!confirm("Bạn có muốn xóa ảnh kỷ niệm này?")) return;
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/photos/${photoId}`,
        {
          method: "DELETE",
          headers: getHeaders(),
        }
      );
      if (res.ok) {
        toast.success("Xóa ảnh kỷ niệm thành công! 🗑️");
        fetchPhotosForEvent(eventId);
      } else {
        toast.error("Không thể xóa ảnh");
      }
    } catch {
      toast.error("Lỗi kết nối");
    }
  };

  // Calendar calculations
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
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };

  const nextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };

  const selectedEvents = selectedDate ? events.filter((e) => e.event_date === selectedDate) : [];

  // Load photos when opening day detail
  const handleOpenDayDetail = (dateStr: string) => {
    setSelectedDate(dateStr);
    const dayEvents = events.filter((e) => e.event_date === dateStr);
    dayEvents.forEach((event) => {
      fetchPhotosForEvent(event.id);
    });
    setShowDayDetail(true);
  };

  const handleOpenEditModal = (event: LoveEvent, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditFormData({
      id: event.id,
      title: event.title,
      event_type: event.event_type,
      event_date: event.event_date,
      event_time: event.event_time ? event.event_time.slice(0, 5) : "",
      description: event.description || "",
      location_name: event.location_name || "",
    });
    setShowEdit(true);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Top Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="font-heading text-2xl md:text-3xl font-bold flex items-center gap-2 text-foreground">
            📅 Lịch Yêu Thương
          </h1>
          <p className="text-muted-foreground text-xs md:text-sm mt-1">Lưu trữ các cột mốc tình yêu và kỷ niệm đẹp đẽ</p>
        </div>
        <Button
          size="sm"
          className="shadow-rose hover:scale-[1.02] active:scale-[0.98] transition-all duration-200"
          onClick={() => {
            setFormData((prev) => ({ ...prev, event_date: todayStr }));
            setShowCreate(true);
          }}
        >
          + Sự kiện mới
        </Button>
      </div>

      {/* Main Calendar Card */}
      <div
        className="bg-card rounded-2xl p-6 shadow-card border border-border"
        style={{ transition: "box-shadow 0.3s ease" }}
      >
        {/* Navigation month/year */}
        <div className="flex justify-between items-center mb-6">
          <button
            onClick={prevMonth}
            className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-muted text-muted-foreground text-lg transition-all duration-200 active:scale-95"
          >
            ←
          </button>
          <span className="font-heading font-bold text-lg text-foreground flex items-center gap-2">
            ✨ {MONTHS[currentMonth]} {currentYear}
          </span>
          <button
            onClick={nextMonth}
            className="w-10 h-10 flex items-center justify-center rounded-full hover:bg-muted text-muted-foreground text-lg transition-all duration-200 active:scale-95"
          >
            →
          </button>
        </div>

        {/* Days Header */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {DAYS.map((d) => (
            <div
              key={d}
              className="text-center text-xs font-semibold text-muted-foreground py-2 tracking-wider"
            >
              {d}
            </div>
          ))}
        </div>

        {/* Calendar Days Grid */}
        <div className="grid grid-cols-7 gap-1">
          {calendarDays.map((day, i) => {
            if (day === null) return <div key={`empty-${i}`} className="min-h-[50px] md:min-h-[70px]" />;
            const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
            const dayEvents = getEventsForDay(day);
            const isToday = dateStr === todayStr;

            return (
              <button
                key={day}
                type="button"
                onClick={() => handleOpenDayDetail(dateStr)}
                className={`group relative min-h-[55px] md:min-h-[75px] p-2 text-left flex flex-col justify-between rounded-xl border border-transparent transition-all duration-200 cursor-pointer ${
                  isToday
                    ? "bg-rose-50/50 dark:bg-rose-950/20 border-rose-200 dark:border-rose-900/30"
                    : "hover:bg-muted hover:border-border"
                }`}
              >
                <span
                  className={`text-xs font-bold w-6 h-6 flex items-center justify-center rounded-full transition-all ${
                    isToday
                      ? "bg-gradient-to-r from-rose-400 to-pink-500 text-white shadow-rose"
                      : "text-foreground group-hover:text-rose-500"
                  }`}
                >
                  {day}
                </span>

                {/* Event list snippet */}
                {dayEvents.length > 0 && (
                  <div className="w-full flex flex-wrap gap-1 mt-1">
                    {dayEvents.slice(0, 3).map((e, j) => (
                      <span
                        key={j}
                        title={e.title}
                        className="text-sm p-0.5 rounded-md hover:scale-110 transition-transform"
                      >
                        {e.icon}
                      </span>
                    ))}
                    {dayEvents.length > 3 && (
                      <span className="text-[10px] font-bold text-muted-foreground self-center">
                        +{dayEvents.length - 3}
                      </span>
                    )}
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Day Detail Slide-up/Modal */}
      {showDayDetail && selectedDate && (
        <div
          className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-end md:items-center justify-center z-50 p-4 transition-all duration-300"
          onClick={(e) => e.target === e.currentTarget && setShowDayDetail(false)}
        >
          <div className="bg-card rounded-t-3xl md:rounded-2xl p-6 w-full max-w-2xl max-h-[85vh] md:max-h-[80vh] overflow-y-auto shadow-card border border-border animate-slide-up">
            {/* Modal Header */}
            <div className="flex justify-between items-center mb-6 pb-2 border-b border-border">
              <div>
                <h3 className="font-heading text-lg font-bold text-foreground flex items-center gap-2">
                  📅 Chi tiết ngày {selectedDate.split("-").reverse().join("/")}
                </h3>
              </div>
              <button
                onClick={() => setShowDayDetail(false)}
                className="w-8 h-8 rounded-full flex items-center justify-center hover:bg-muted text-muted-foreground text-sm font-bold transition-all"
              >
                ✕
              </button>
            </div>

            {/* Event Lists on that Day */}
            {selectedEvents.length === 0 ? (
              <div className="text-center py-8">
                <span className="text-4xl block mb-2">🎈</span>
                <p className="text-muted-foreground text-sm">Chưa có sự kiện nào cho ngày này.</p>
                <button
                  type="button"
                  onClick={() => {
                    setFormData({ ...formData, event_date: selectedDate });
                    setShowCreate(true);
                  }}
                  className="mt-3 text-rose-500 font-semibold hover:underline text-sm cursor-pointer"
                >
                  Tạo sự kiện mới?
                </button>
              </div>
            ) : (
              <div className="space-y-6">
                {selectedEvents.map((event) => {
                  const photos = photosByEvent[event.id] || [];
                  return (
                    <div
                      key={event.id}
                      className="bg-muted/30 border border-border rounded-2xl p-5 space-y-4 hover:shadow-sm transition-all"
                    >
                      {/* Event Row details */}
                      <div className="flex items-start gap-3 justify-between">
                        <div className="flex items-start gap-3">
                          <span className="text-2xl p-2 bg-rose-100/50 dark:bg-rose-950/20 rounded-xl">
                            {event.icon}
                          </span>
                          <div>
                            <h4 className="font-heading font-bold text-base text-foreground">
                              {event.title}
                            </h4>
                            <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted-foreground mt-1">
                              {event.event_time && (
                                <span className="flex items-center gap-1">🕐 {event.event_time.slice(0, 5)}</span>
                              )}
                              {event.location_name && (
                                <span className="flex items-center gap-1">📍 {event.location_name}</span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Event actions */}
                        <div className="flex gap-2">
                          <button
                            onClick={(e) => handleOpenEditModal(event, e)}
                            title="Chỉnh sửa"
                            className="p-2 hover:bg-muted rounded-full text-muted-foreground hover:text-rose-500 transition-all cursor-pointer text-xs"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleDeleteEvent(event.id)}
                            title="Xóa"
                            className="p-2 hover:bg-muted rounded-full text-muted-foreground hover:text-red-500 transition-all cursor-pointer text-xs"
                          >
                            🗑️
                          </button>
                        </div>
                      </div>

                      {/* Description if any */}
                      {event.description && (
                        <p className="text-sm text-card-foreground/80 pl-2 border-l-2 border-rose-300 dark:border-rose-900/50 py-0.5">
                          {event.description}
                        </p>
                      )}

                      {/* Attached memories / photos */}
                      <div className="space-y-2 pt-2">
                        <div className="flex justify-between items-center">
                          <h5 className="text-xs font-bold tracking-wider text-muted-foreground uppercase flex items-center gap-1">
                            📸 Ảnh Kỷ Niệm ({photos.length})
                          </h5>
                          
                          {/* File Uploader button */}
                          <label className="text-xs font-semibold text-rose-500 hover:underline cursor-pointer flex items-center gap-1">
                            {isUploading === event.id ? (
                              <span className="flex items-center gap-1 animate-pulse">
                                ⏳ Đang tải...
                              </span>
                            ) : (
                              <>+ Thêm ảnh</>
                            )}
                            <input
                              type="file"
                              accept="image/*"
                              className="hidden"
                              disabled={isUploading !== null}
                              ref={(el) => { fileInputRefs.current[event.id] = el; }}
                              onChange={(e) => handleFileChange(event.id, event.event_date, e.target.files)}
                            />
                          </label>
                        </div>

                        {/* Photo list grid */}
                        {photos.length === 0 ? (
                          <div
                            onClick={() => fileInputRefs.current[event.id]?.click()}
                            className="border-2 border-dashed border-border hover:border-rose-300 dark:hover:border-rose-900/50 rounded-xl p-6 text-center cursor-pointer transition-all duration-200"
                          >
                            <span className="text-2xl block mb-1 opacity-70">📷</span>
                            <p className="text-xs text-muted-foreground">Kéo thả hoặc nhấp vào đây để đăng ảnh kỷ niệm của hai bạn</p>
                          </div>
                        ) : (
                          <div className="grid grid-cols-3 gap-2">
                            {photos.map((photo) => (
                              <div
                                key={photo.id}
                                className="group relative aspect-square rounded-xl overflow-hidden bg-muted border border-border shadow-sm"
                              >
                                <img
                                  src={photo.original_url}
                                  alt={photo.caption || "Memory"}
                                  className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                                  loading="lazy"
                                />
                                <button
                                  type="button"
                                  onClick={() => handleDeletePhoto(photo.id, event.id)}
                                  className="absolute top-1 right-1 w-6 h-6 bg-black/60 hover:bg-black/80 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 cursor-pointer text-[10px]"
                                  title="Xóa ảnh"
                                >
                                  ✕
                                </button>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    onClick={() => {
                      setFormData({ ...formData, event_date: selectedDate });
                      setShowCreate(true);
                    }}
                    fullWidth
                  >
                    + Tạo thêm sự kiện
                  </Button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Create Event Modal */}
      {showCreate && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center z-[60] p-4"
          onClick={(e) => e.target === e.currentTarget && setShowCreate(false)}
        >
          <div className="bg-card rounded-2xl p-6 w-full max-w-md max-h-[85vh] overflow-y-auto shadow-card border border-border animate-scale-up">
            <h2 className="font-heading text-xl font-bold mb-4 flex items-center gap-2 text-foreground">
              ✨ Tạo sự kiện mới
            </h2>

            <div className="space-y-4">
              <FormField
                label="Tên sự kiện"
                name="title"
                type="text"
                placeholder="Ví dụ: Valentine's Day 💕"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
              />

              <div>
                <label className="text-xs font-semibold text-muted-foreground block mb-2 uppercase tracking-wider">
                  Loại sự kiện
                </label>
                <div className="flex flex-wrap gap-2">
                  {EVENT_TYPES.map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setFormData({ ...formData, event_type: t.id })}
                      className={`px-3 py-2 rounded-full border text-xs font-semibold transition-all duration-200 cursor-pointer flex items-center gap-1 ${
                        formData.event_type === t.id
                          ? "border-rose-400 bg-rose-100/50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 shadow-sm"
                          : "border-border bg-transparent text-foreground hover:bg-muted"
                      }`}
                    >
                      {t.icon} {t.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <FormField
                  label="Ngày"
                  name="event_date"
                  type="date"
                  value={formData.event_date}
                  onChange={(e) => setFormData({ ...formData, event_date: e.target.value })}
                  required
                />
                <FormField
                  label="Giờ (không bắt buộc)"
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
                placeholder="Ví dụ: Hồ Gươm, Hà Nội"
                value={formData.location_name}
                onChange={(e) => setFormData({ ...formData, location_name: e.target.value })}
              />

              <div>
                <label className="text-xs font-semibold text-muted-foreground block mb-1 uppercase tracking-wider">
                  Mô tả sự kiện
                </label>
                <textarea
                  className="w-full rounded-xl border border-border bg-input text-foreground text-sm p-3 focus:outline-rose-400 focus:outline focus:outline-2"
                  rows={3}
                  placeholder="Ghi chú gì đó cho ngày đặc biệt này..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>

              <div className="flex gap-3 pt-2">
                <Button variant="ghost" onClick={() => setShowCreate(false)} className="flex-1">
                  Hủy
                </Button>
                <Button onClick={handleCreateEvent} isLoading={isLoading} className="flex-2 shadow-rose">
                  Tạo sự kiện 🎉
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Event Modal */}
      {showEdit && (
        <div
          className="fixed inset-0 bg-black/50 backdrop-blur-xs flex items-center justify-center z-[60] p-4"
          onClick={(e) => e.target === e.currentTarget && setShowEdit(false)}
        >
          <div className="bg-card rounded-2xl p-6 w-full max-w-md max-h-[85vh] overflow-y-auto shadow-card border border-border animate-scale-up">
            <h2 className="font-heading text-xl font-bold mb-4 flex items-center gap-2 text-foreground">
              ✏️ Chỉnh sửa sự kiện
            </h2>

            <div className="space-y-4">
              <FormField
                label="Tên sự kiện"
                name="title"
                type="text"
                value={editFormData.title}
                onChange={(e) => setEditFormData({ ...editFormData, title: e.target.value })}
                required
              />

              <div>
                <label className="text-xs font-semibold text-muted-foreground block mb-2 uppercase tracking-wider">
                  Loại sự kiện
                </label>
                <div className="flex flex-wrap gap-2">
                  {EVENT_TYPES.map((t) => (
                    <button
                      key={t.id}
                      type="button"
                      onClick={() => setEditFormData({ ...editFormData, event_type: t.id })}
                      className={`px-3 py-2 rounded-full border text-xs font-semibold transition-all duration-200 cursor-pointer flex items-center gap-1 ${
                        editFormData.event_type === t.id
                          ? "border-rose-400 bg-rose-100/50 dark:bg-rose-950/20 text-rose-600 dark:text-rose-400 shadow-sm"
                          : "border-border bg-transparent text-foreground hover:bg-muted"
                      }`}
                    >
                      {t.icon} {t.label}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <FormField
                  label="Ngày"
                  name="event_date"
                  type="date"
                  value={editFormData.event_date}
                  onChange={(e) => setEditFormData({ ...editFormData, event_date: e.target.value })}
                  required
                />
                <FormField
                  label="Giờ"
                  name="event_time"
                  type="time"
                  value={editFormData.event_time}
                  onChange={(e) => setEditFormData({ ...editFormData, event_time: e.target.value })}
                />
              </div>

              <FormField
                label="Địa điểm"
                name="location_name"
                type="text"
                value={editFormData.location_name}
                onChange={(e) => setEditFormData({ ...editFormData, location_name: e.target.value })}
              />

              <div>
                <label className="text-xs font-semibold text-muted-foreground block mb-1 uppercase tracking-wider">
                  Mô tả sự kiện
                </label>
                <textarea
                  className="w-full rounded-xl border border-border bg-input text-foreground text-sm p-3 focus:outline-rose-400 focus:outline focus:outline-2"
                  rows={3}
                  value={editFormData.description}
                  onChange={(e) => setEditFormData({ ...editFormData, description: e.target.value })}
                />
              </div>

              <div className="flex gap-3 pt-2">
                <Button variant="ghost" onClick={() => setShowEdit(false)} className="flex-1">
                  Hủy
                </Button>
                <Button onClick={handleEditEvent} isLoading={isLoading} className="flex-2 shadow-rose">
                  Lưu thay đổi ✏️
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
