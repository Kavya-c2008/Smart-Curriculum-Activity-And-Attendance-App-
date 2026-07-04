import qrcode

student_id = "S101"

img = qrcode.make(student_id)

img.save("student_qr.png")

print("QR Code Generated")