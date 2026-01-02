class Staff {
  final int id;
  final String staffId;
  final String firstName;
  final String lastName;
  final String username;
  final String email;
  final String address;
  final DateTime createdAt;
  final DateTime updatedAt;

  Staff({
    required this.id,
    required this.staffId,
    required this.firstName,
    required this.lastName,
    required this.username,
    required this.email,
    required this.address,
    required this.createdAt,
    required this.updatedAt,
  });

  factory Staff.fromJson(Map<String, dynamic> json) {
    return Staff(
      id: json['id'],
      staffId: json['staff_id'] ?? '',
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      username: json['username'] ?? '',
      email: json['email'] ?? '',
      address: json['address'] ?? '',
      createdAt: DateTime.parse(json['created_at']),
      updatedAt: DateTime.parse(json['updated_at']),
    );
  }
}
