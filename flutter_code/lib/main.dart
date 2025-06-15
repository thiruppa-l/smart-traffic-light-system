import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_database/firebase_database.dart';
import 'package:google_fonts/google_fonts.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();
  runApp(SmartTrafficLightApp());
}

class SmartTrafficLightApp extends StatefulWidget {
  @override
  _SmartTrafficLightAppState createState() => _SmartTrafficLightAppState();
}

class _SmartTrafficLightAppState extends State<SmartTrafficLightApp> {
  final DatabaseReference dbRef = FirebaseDatabase.instance.ref("junctions");

  Map<int, Map<String, dynamic>> junctions = {};

  @override
  void initState() {
    super.initState();
    listenToFirebase();
  }

  void listenToFirebase() {
    dbRef.onValue.listen((event) {
      if (event.snapshot.value != null) {
        Map<dynamic, dynamic> data =
        event.snapshot.value as Map<dynamic, dynamic>;
        setState(() {
          junctions = data.map((key, value) {
            return MapEntry(
              int.parse(key.toString().split('_')[1]),
              Map<String, dynamic>.from(value),
            );
          });
        });
      }
    });
  }

  Color getColor(String state) {
    switch (state) {
      case "Red":
        return Colors.red;
      case "Yellow":
        return Colors.amber;
      case "Green":
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  Widget getTrafficSignal(String state) {
    return SizedBox(
      width: 20,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          _buildLight(state == "Red" ? Colors.red : Colors.red.withOpacity(0.2)),
          SizedBox(height: 4),
          _buildLight(state == "Yellow" ? Colors.amber : Colors.amber.withOpacity(0.2)),
          SizedBox(height: 4),
          _buildLight(state == "Green" ? Colors.green : Colors.green.withOpacity(0.2)),
        ],
      ),
    );
  }

  Widget _buildLight(Color color) {
    return Container(
      width: 20,
      height: 20,
      decoration: BoxDecoration(
        color: color,
        shape: BoxShape.circle,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        textTheme: GoogleFonts.poppinsTextTheme(Theme.of(context).textTheme),
      ),
      home: Scaffold(
        body: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Colors.blue.shade50, Colors.white],
            ),
          ),
          child: Padding(
            padding: EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(height: 40),
                Text(
                  "Traffic Light System",
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue.shade900,
                  ),
                ),
                SizedBox(height: 10),
                Text(
                  "Real-time junction states",
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.blue.shade700,
                  ),
                ),
                SizedBox(height: 20),
                Expanded(
                  child: ListView.builder(
                    itemCount: junctions.length,
                    itemBuilder: (context, index) {
                      var junction = junctions[index] ?? {};
                      return AnimatedContainer(
                        duration: Duration(milliseconds: 300),
                        margin: EdgeInsets.symmetric(vertical: 8),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(15),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black12,
                              blurRadius: 10,
                              offset: Offset(0, 4),
                            )
                          ],
                        ),
                        child: ListTile(
                          contentPadding: EdgeInsets.all(10),
                          leading: getTrafficSignal(junction['state']),
                          title: Text(
                            "Junction ${index + 1}",
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.blue.shade900,
                            ),
                          ),
                          subtitle: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              SizedBox(height: 4),
                              Text(
                                "State: ${junction['state']}",
                                style: TextStyle(
                                  fontSize: 16,
                                  color: Colors.grey.shade700,
                                ),
                              ),
                              SizedBox(height: 4),
                              Text(
                                "Density: ${junction['density']}",
                                style: TextStyle(
                                  fontSize: 16,
                                  color: Colors.grey.shade700,
                                ),
                              ),
                              SizedBox(height: 8),
                              LinearProgressIndicator(
                                value: (junction['density'] ?? 0) / 10,
                                backgroundColor: Colors.grey.shade200,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  getColor(junction['state']),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
