public class Note
{
    public string NoteContent { get; set; }
    public String NoteTime { get; set; } // If you need to parse this as a DateTime, change to DateTime type
    public string NoteId { get; set; }
    public string NoteTitle { get; set; }
    public string NoteCategory { get; set; }
    public string UserId { get; set; }
    public string Status { get; set; }
}
