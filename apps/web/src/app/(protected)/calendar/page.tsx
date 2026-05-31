"use client";

import { useState, useMemo, useRef, useEffect } from "react";
import { Button } from "@/components/atoms/button";
import { FormField } from "@/components/molecules/form-field";
import { toast } from "sonner";
import {
  useEvents,
  useCreateEvent,
  useUpdateEvent,
  useDeleteEvent,
  LoveEvent,
} from "@/hooks/use-events";
import {
  useEventPhotos,
  useAddPhoto,
  useDeletePhoto,
} from "@/hooks/use-photos";

const EVENT_TYPES = [
  { id: "date", icon: "❤️", label: "Hẹn hò" },
  { id: "anniversary", icon: "💍", label: "Kỷ niệm" },
  { id: "travel", icon: "✈️", label: "Du lịch" },
  { id: "birthday", icon: "🎂", label: "Sinh nhật" },
  { id: "custom", icon: "⭐", label: "Khác" },
];

const REMINDER_OPTIONS = [
  { value: "", label: "Không nhắc nhở" },
  { value: "15m", label: "15 phút trước" },
  { value: "1h", label: "1 giờ trước" },
  { value: "1d", label: "1 ngày trước" },
  { value: "1w", label: "1 tuần trước" },
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
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<"month" | "week">("month");
  
  // Modals state
  const [showCreate, setShowCreate] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [showDayDetail, setShowDayDetail] = useState(false);
  
  const [selectedEventIdForPhotos, setSelectedEventIdForPhotos] = useState<string | null>(null);
  const fileInputRefs = useRef<Record<string, HTMLInputElement | null>>({});

  const [formData, setFormData] = useState({
    title: "",
    event_type: "date",
    event_date: "",
    event_time: "",
    description: "",
    location_name: "",
    latitude: "",
    longitude: "",
    is_recurring: false,
    reminder_before: "",
  });

  const [editFormData, setEditFormData] = useState({
    id: "",
    title: "",
    event_type: "date",
    event_date: "",
    event_time: "",
    description: "",
    location_name: "",
    latitude: "",
    longitude: "",
    is_recurring: false,
    reminder_before: "",
  });

  // Queries & Mutations
  const { data: events = [], isLoading: isEventsLoading } = useEvents(currentYear, currentMonth + 1);
  const createEventMutation = useCreateEvent();
  const updateEventMutation = useUpdateEvent();
  const deleteEventMutation = useDeleteEvent();

  const { data: eventPhotos = [] } = useEventPhotos(selectedEventIdForPhotos || "");
  const addPhotoMutation = useAddPhoto();
  const deletePhotoMutation = useDeletePhoto();

  // Day detail auto-select
  const selectedEvents = useMemo(() => {
    return selectedDate ? events.filter((e) => e.event_date === selectedDate) : [];
  }, [events, selectedDate]);

  // Load photos when selectedEvents change or an event is selected
  useEffect(() => {
    if (selectedEvents.length > 0) {
      if (!selectedEventIdForPhotos || !selectedEvents.some((e) => e.id === selectedEventIdForPhotos)) {
        setSelectedEventIdForPhotos(selectedEvents[0].id);
      }
    } else {
      setSelectedEventIdForPhotos(null);
    }
  }, [selectedEvents, selectedEventIdForPhotos]);

  const handleCreateEvent = async () => {
    if (!formData.title || !formData.event_date) return;
    
    try {
      await createEventMutation.mutateAsync({
        title: formData.title,
        event_type: formData.event_type,
        event_date: formData.event_date,
        event_time: formData.event_time || undefined,
        description: formData.description || undefined,
        location_name: formData.location_name || undefined,
        latitude: formData.latitude ? parseFloat(formData.latitude) : undefined,
        longitude: formData.longitude ? parseFloat(formData.longitude) : undefined,
        is_recurring: formData.is_recurring,
        recurrence_rule: formData.is_recurring ? "YEARLY" : undefined,
        reminder_before: formData.reminder_before || undefined,
      });

      toast.success("Tạo sự kiện thành công! 🎉");
      setShowCreate(false);
      setFormData({
        title: "",
        event_type: "date",
        event_date: "",
        event_time: "",
        description: "",
        location_name: "",
        latitude: "",
        longitude: "",
        is_recurring: false,
        reminder_before: "",
      });
      if (selectedDate === formData.event_date) {
        setSelectedDate(formData.event_date);
      }
    } catch (err: any) {
      toast.error(err.message || "Lỗi tạo sự kiện");
    }
  };

  const handleEditEvent = async () => {
    if (!editFormData.title || !editFormData.event_date) return;
    
    try {
      await updateEventMutation.mutateAsync({
        id: editFormData.id,
        title: editFormData.title,
        event_type: editFormData.event_type,
        event_date: editFormData.event_date,
        event_time: editFormData.event_time || undefined,
        description: editFormData.description || undefined,
        location_name: editFormData.location_name || undefined,
        latitude: editFormData.latitude ? parseFloat(editFormData.latitude) : undefined,
        longitude: editFormData.longitude ? parseFloat(editFormData.longitude) : undefined,
        is_recurring: editFormData.is_recurring,
        recurrence_rule: editFormData.is_recurring ? "YEARLY" : undefined,
        reminder_before: editFormData.reminder_before || undefined,
      });

      toast.success("Cập nhật sự kiện thành công! ✏️");
      setShowEdit(false);
    } catch (err: any) {
      toast.error(err.message || "Lỗi cập nhật sự kiện");
    }
  };

  const handleDeleteEvent = async (event: LoveEvent) => {
    if (!confirm("Bạn có chắc chắn muốn xóa sự kiện này không?")) return;
    try {
      await deleteEventMutation.mutateAsync({ id: event.id, eventDate: event.event_date });
      toast.success("Xóa sự kiện thành công! 🗑️");
      const updatedSelectedEvents = events.filter((e) => e.id !== event.id && e.event_date === selectedDate);
      if (updatedSelectedEvents.length === 0) {
        setShowDayDetail(false);
      }
    } catch (err: any) {
      toast.error(err.message || "Lỗi xóa sự kiện");
    }
  };

  // Photo uploading flow
  const handleFileChange = async (eventId: string, eventDate: string, fileList: FileList | null) => {
    if (!fileList || fileList.length === 0) return;
    const file = fileList[0];
    
    const toastId = toast.loading("Đang tải ảnh kỷ niệm lên...");
    try {
      // 1. Get presigned upload URL
      const presignedRes = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/storage/presigned-url`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("access_token") || ""}`,
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
      await addPhotoMutation.mutateAsync({
        s3_key: s3Key,
        original_url: file_url,
        event_id: eventId,
        caption: file.name.split(".")[0],
        photo_date: eventDate,
      });

      toast.success("Tải kỷ niệm lên thành công! 📸", { id: toastId });
    } catch (err: any) {
      toast.error(err.message || "Đã xảy ra lỗi khi tải ảnh lên", { id: toastId });
    }
  };

  const handleDeletePhoto = async (photoId: string, eventId: string) => {
    if (!confirm("Bạn có muốn xóa ảnh kỷ niệm này?")) return;
    try {
      await deletePhotoMutation.mutateAsync({ id: photoId, eventId });
      toast.success("Xóa ảnh kỷ niệm thành công! 🗑️");
    } catch {
      toast.error("Không thể xóa ảnh");
    }
  };

  // Calendar math
  const calendarDays = useMemo(() => {
    const firstDay = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();
    const days: (number | null)[] = [];
    for (let i = 0; i < firstDay; i++) days.push(null);
    for (let i = 1; i <= daysInMonth; i++) days.push(i);
    return days;
  }, [currentYear, currentMonth]);

  // Week View math
  const currentWeekDays = useMemo(() => {
    const current = selectedDate ? new Date(selectedDate) : new Date();
    const dayOfWeek = current.getDay(); // 0 is Sunday
    const startOfWeek = new Date(current);
    startOfWeek.setDate(current.getDate() - dayOfWeek); // set to Sunday

    const days = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(startOfWeek);
      d.setDate(startOfWeek.getDate() + i);
      days.push(d);
    }
    return days;
  }, [selectedDate]);

  const getEventsForDate = (dateStr: string) => {
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

  const handleOpenDayDetail = (dateStr: string) => {
    setSelectedDate(dateStr);
    const dayEvents = events.filter((e) => e.event_date === dateStr);
    if (dayEvents.length > 0) {
      setSelectedEventIdForPhotos(dayEvents[0].id);
    } else {
      setSelectedEventIdForPhotos(null);
    }
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
      latitude: event.latitude ? String(event.latitude) : "",
      longitude: event.longitude ? String(event.longitude) : "",
      is_recurring: event.is_recurring,
      reminder_before: event.reminder_before || "",
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
        <div className="flex items-center gap-2">
          {/* Month/Week Toggle */}
          <div className="flex bg-muted p-1 rounded-xl border border-border">
            <button
              onClick={() => setViewMode("month")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                viewMode === "month"
                  ? "bg-card text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Tháng
            </button>
            <button
              onClick={() => setViewMode("week")}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                viewMode === "week"
                  ? "bg-card text-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Tuần
            </button>
          </div>

          <Button
            size="sm"
            className="shadow-rose hover:scale-[1.02] active:scale-[0.98] transition-all duration-200"
            onClick={() => {
              setFormData((prev) => ({ ...prev, event_date: selectedDate || todayStr }));
              setShowCreate(true);
            }}
          >
            + Sự kiện mới
          </Button>
        </div>
      </div>

      {/* Main Calendar Card */}
      <div className="bg-card rounded-2xl p-6 shadow-card border border-border transition-all">
        {/* Navigation month/year */}
        {viewMode === "month" ? (
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
        ) : (
          <div className="flex justify-between items-center mb-6">
            <span className="font-heading font-bold text-lg text-foreground flex items-center gap-2">
              📅 Tuần Hiện Tại (Tháng {currentMonth + 1} {currentYear})
            </span>
            <p className="text-xs text-muted-foreground">Nhấp vào một ngày để xem chi tiết</p>
          </div>
        )}

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

        {/* Month View Grid */}
        {viewMode === "month" ? (
          <div className="grid grid-cols-7 gap-1">
            {isEventsLoading ? (
              Array.from({ length: 35 }).map((_, idx) => (
                <div
                  key={idx}
                  className="min-h-[55px] md:min-h-[75px] bg-muted/20 animate-pulse rounded-xl"
                />
              ))
            ) : (
              calendarDays.map((day, i) => {
                if (day === null) return <div key={`empty-${i}`} className="min-h-[50px] md:min-h-[70px]" />;
                const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
                const dayEvents = getEventsForDate(dateStr);
                const isToday = dateStr === todayStr;
                const isSelected = dateStr === selectedDate;

                return (
                  <button
                    key={day}
                    type="button"
                    onClick={() => handleOpenDayDetail(dateStr)}
                    className={`group relative min-h-[55px] md:min-h-[75px] p-2 text-left flex flex-col justify-between rounded-xl border border-transparent transition-all duration-200 cursor-pointer ${
                      isSelected
                        ? "bg-rose-100/30 dark:bg-rose-950/20 border-rose-300 dark:border-rose-900"
                        : isToday
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

                    {dayEvents.length > 0 && (
                      <div className="w-full flex flex-wrap gap-1 mt-1">
                        {dayEvents.slice(0, 3).map((e, j) => (
                          <span key={j} title={e.title} className="text-sm p-0.5 rounded-md hover:scale-115 transition-transform">
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
              })
            )}
          </div>
        ) : (
          /* Week View Grid */
          <div className="grid grid-cols-7 gap-1">
            {currentWeekDays.map((dateObj, i) => {
              const dateStr = `${dateObj.getFullYear()}-${String(dateObj.getMonth() + 1).padStart(2, "0")}-${String(dateObj.getDate()).padStart(2, "0")}`;
              const dayEvents = getEventsForDate(dateStr);
              const isToday = dateStr === todayStr;
              const isSelected = dateStr === selectedDate;

              return (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleOpenDayDetail(dateStr)}
                  className={`group relative min-h-[90px] p-3 text-left flex flex-col justify-between rounded-xl border border-transparent transition-all duration-200 cursor-pointer ${
                    isSelected
                      ? "bg-rose-100/30 dark:bg-rose-950/20 border-rose-300 dark:border-rose-900"
                      : isToday
                      ? "bg-rose-50/50 dark:bg-rose-950/20 border-rose-200 dark:border-rose-900/30"
                      : "bg-muted/10 border-border hover:bg-muted"
                  }`}
                >
                  <span
                    className={`text-xs font-bold w-6 h-6 flex items-center justify-center rounded-full transition-all ${
                      isToday
                        ? "bg-gradient-to-r from-rose-400 to-pink-500 text-white shadow-rose"
                        : "text-foreground group-hover:text-rose-500"
                    }`}
                  >
                    {dateObj.getDate()}
                  </span>

                  <div className="w-full mt-2 flex flex-col gap-1">
                    {dayEvents.slice(0, 2).map((e, j) => (
                      <div key={j} className="text-[10px] bg-rose-100/40 dark:bg-rose-950/30 border border-rose-200/50 dark:border-rose-900/30 rounded-md px-1 py-0.5 truncate flex items-center gap-1 text-foreground/80">
                        <span>{e.icon}</span>
                        <span className="truncate">{e.title}</span>
                      </div>
                    ))}
                    {dayEvents.length > 2 && (
                      <span className="text-[9px] font-bold text-muted-foreground pl-1">
                        +{dayEvents.length - 2} sự kiện khác
                      </span>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        )}
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
                  const isCurrentPhotosEvent = selectedEventIdForPhotos === event.id;
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
                            <h4 className="font-heading font-bold text-base text-foreground flex items-center gap-1.5">
                              {event.title}
                              {event.is_recurring && (
                                <span className="text-xs bg-rose-100 dark:bg-rose-950/30 text-rose-500 px-2 py-0.5 rounded-full font-bold">
                                  🔁 Hàng năm
                                </span>
                              )}
                            </h4>
                            <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-muted-foreground mt-1">
                              {event.event_time && (
                                <span className="flex items-center gap-1">🕐 {event.event_time.slice(0, 5)}</span>
                              )}
                              {event.location_name && (
                                <span className="flex items-center gap-1">📍 {event.location_name}</span>
                              )}
                              {event.latitude && event.longitude && (
                                <span className="flex items-center gap-1 opacity-70">🧭 ({event.latitude}, {event.longitude})</span>
                              )}
                              {event.reminder_before && (
                                <span className="flex items-center gap-1">🔔 {REMINDER_OPTIONS.find(o => o.value === event.reminder_before)?.label || event.reminder_before}</span>
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
                            onClick={() => handleDeleteEvent(event)}
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
                          <button
                            onClick={() => setSelectedEventIdForPhotos(event.id)}
                            className={`text-xs font-bold tracking-wider uppercase flex items-center gap-1 transition-all ${
                              isCurrentPhotosEvent ? "text-rose-500" : "text-muted-foreground hover:text-foreground"
                            }`}
                          >
                            📸 Ảnh Kỷ Niệm {isCurrentPhotosEvent && `(${eventPhotos.length})`}
                          </button>
                          
                          {/* File Uploader button */}
                          <label className="text-xs font-semibold text-rose-500 hover:underline cursor-pointer flex items-center gap-1">
                            {addPhotoMutation.isPending && isCurrentPhotosEvent ? (
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
                              disabled={addPhotoMutation.isPending}
                              ref={(el) => { fileInputRefs.current[event.id] = el; }}
                              onChange={(e) => handleFileChange(event.id, event.event_date, e.target.files)}
                            />
                          </label>
                        </div>

                        {/* Photo list grid (on-demand loading) */}
                        {isCurrentPhotosEvent ? (
                          eventPhotos.length === 0 ? (
                            <div
                              onClick={() => fileInputRefs.current[event.id]?.click()}
                              className="border-2 border-dashed border-border hover:border-rose-300 dark:hover:border-rose-900/50 rounded-xl p-6 text-center cursor-pointer transition-all duration-200"
                            >
                              <span className="text-2xl block mb-1 opacity-70">📷</span>
                              <p className="text-xs text-muted-foreground">Kéo thả hoặc nhấp vào đây để đăng ảnh kỷ niệm của hai bạn</p>
                            </div>
                          ) : (
                            <div className="grid grid-cols-3 gap-2">
                              {eventPhotos.map((photo) => (
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
                          )
                        ) : (
                          <button
                            onClick={() => setSelectedEventIdForPhotos(event.id)}
                            className="w-full py-2 bg-muted/40 hover:bg-muted/70 rounded-xl border border-border/50 text-xs font-semibold text-muted-foreground cursor-pointer transition-all"
                          >
                            Hiển thị album ảnh kỷ niệm 📁
                          </button>
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

              {/* Coordinates Input */}
              <div className="grid grid-cols-2 gap-3 bg-muted/20 border border-border p-3 rounded-xl">
                <FormField
                  label="Vĩ độ (Latitude)"
                  name="latitude"
                  type="number"
                  placeholder="21.0285"
                  value={formData.latitude}
                  onChange={(e) => setFormData({ ...formData, latitude: e.target.value })}
                />
                <FormField
                  label="Kinh độ (Longitude)"
                  name="longitude"
                  type="number"
                  placeholder="105.8542"
                  value={formData.longitude}
                  onChange={(e) => setFormData({ ...formData, longitude: e.target.value })}
                />
              </div>

              {/* Reminder options */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-muted-foreground block mb-1.5 uppercase tracking-wider">
                    Nhắc nhở
                  </label>
                  <select
                    value={formData.reminder_before}
                    onChange={(e) => setFormData({ ...formData, reminder_before: e.target.value })}
                    className="w-full rounded-xl border border-border bg-input text-foreground text-sm p-3 focus:outline-rose-400 focus:outline focus:outline-2"
                  >
                    {REMINDER_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>
                        {o.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Recurrence Checkbox */}
                <div className="flex items-center pt-5 pl-2">
                  <label className="flex items-center gap-2 text-xs font-semibold text-muted-foreground cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={formData.is_recurring}
                      onChange={(e) => setFormData({ ...formData, is_recurring: e.target.checked })}
                      className="w-4 h-4 rounded-md border-border text-rose-500 focus:ring-rose-400"
                    />
                    Lặp lại hàng năm 🔁
                  </label>
                </div>
              </div>

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
                <Button
                  onClick={handleCreateEvent}
                  isLoading={createEventMutation.isPending}
                  className="flex-2 shadow-rose"
                >
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

              {/* Coordinates Input */}
              <div className="grid grid-cols-2 gap-3 bg-muted/20 border border-border p-3 rounded-xl">
                <FormField
                  label="Vĩ độ (Latitude)"
                  name="latitude"
                  type="number"
                  placeholder="21.0285"
                  value={editFormData.latitude}
                  onChange={(e) => setEditFormData({ ...editFormData, latitude: e.target.value })}
                />
                <FormField
                  label="Kinh độ (Longitude)"
                  name="longitude"
                  type="number"
                  placeholder="105.8542"
                  value={editFormData.longitude}
                  onChange={(e) => setEditFormData({ ...editFormData, longitude: e.target.value })}
                />
              </div>

              {/* Reminder & Recurrence */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-semibold text-muted-foreground block mb-1.5 uppercase tracking-wider">
                    Nhắc nhở
                  </label>
                  <select
                    value={editFormData.reminder_before}
                    onChange={(e) => setEditFormData({ ...editFormData, reminder_before: e.target.value })}
                    className="w-full rounded-xl border border-border bg-input text-foreground text-sm p-3 focus:outline-rose-400 focus:outline focus:outline-2"
                  >
                    {REMINDER_OPTIONS.map((o) => (
                      <option key={o.value} value={o.value}>
                        {o.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center pt-5 pl-2">
                  <label className="flex items-center gap-2 text-xs font-semibold text-muted-foreground cursor-pointer select-none">
                    <input
                      type="checkbox"
                      checked={editFormData.is_recurring}
                      onChange={(e) => setEditFormData({ ...editFormData, is_recurring: e.target.checked })}
                      className="w-4 h-4 rounded-md border-border text-rose-500 focus:ring-rose-400"
                    />
                    Lặp lại hàng năm 🔁
                  </label>
                </div>
              </div>

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
                <Button
                  onClick={handleEditEvent}
                  isLoading={updateEventMutation.isPending}
                  className="flex-2 shadow-rose"
                >
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
