import SwiftUI
import AVFoundation
import AVKit

struct AirPlayButton: UIViewRepresentable {
    func makeUIView(context: Context) -> UIView {
        let routePickerView = AVRoutePickerView()
        routePickerView.backgroundColor = .clear
        routePickerView.tintColor = .white
        routePickerView.activeTintColor = .red
        return routePickerView
    }
    
    func updateUIView(_ uiView: UIView, context: Context) {
        // No need to update anything here
    }
}

struct ContentView: View {
    @State private var isPlaying = false
    @State private var audioPlayer: AVAudioPlayer?
    @State private var isAudioEngineRunning = false
    @State private var isConnectingToSpeaker = false
    @State private var showPhotos = false
    
    let audioEngine = AVAudioEngine()
    var audioInputNode: AVAudioInputNode?
    var audioOutputNode: AVAudioOutputNode?
    
    init() {
        audioInputNode = audioEngine.inputNode
        audioOutputNode = audioEngine.outputNode
    }

    func setupAudioEngine() {
        do {
            let audioSession = AVAudioSession.sharedInstance()
            
            // Set the audio session category to play and record with Bluetooth options
            try audioSession.setCategory(.playAndRecord, options: [.allowBluetoothA2DP, .allowBluetooth, .defaultToSpeaker, .mixWithOthers])
            
            // Activate the audio session
            try audioSession.setActive(true)
            
            let audioFormat = audioEngine.inputNode.inputFormat(forBus: 0)

            audioEngine.connect(audioInputNode!, to: audioOutputNode!, format: audioFormat)
        } catch {
            print("Error setting up audio engine: \(error.localizedDescription)")
        }
    }

    var body: some View {
        NavigationView {
            ZStack {
                Image("background")
                    .resizable()
                    .scaledToFill()
                    .edgesIgnoringSafeArea(.all)
                    .opacity(0.7)

                VStack {
                    Spacer()

                    Button(action: {
                        if isAudioEngineRunning {
                            stopAudioEngine()
                        } else {
                            startAudioEngine()
                        }
                    }) {
                        Text(isAudioEngineRunning ? "End Session" : "Start Session")
                            .padding()
                            .frame(maxWidth: .infinity)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.black, lineWidth: 2)
                                    .background(RoundedRectangle(cornerRadius: 8).foregroundColor(.white))
                            )
                            .foregroundColor(.black)
                            .font(.headline)
                    }
                    .padding()

                    Spacer()

                    // Button to connect to speaker with mic (smaller size)
                    Button(action: {
                        withAnimation {
                            isConnectingToSpeaker.toggle()
                            showPhotos = false
                        }
                    }) {
                        Text("Connect to Speaker with mic")
                            .padding()
                            .frame(maxWidth: .infinity)
                            .background(
                                RoundedRectangle(cornerRadius: 8)
                                    .stroke(Color.black, lineWidth: 2)
                                    .background(RoundedRectangle(cornerRadius: 8).foregroundColor(.white))
                            )
                            .foregroundColor(.black)
                            .font(.subheadline) // Smaller font size
                    }
                    .padding()

                    Spacer()

                    AirPlayButton()
                        .frame(width: 80, height: 80)

                    Spacer()
                }

                // Display photos when isConnectingToSpeaker is true
                if isConnectingToSpeaker {
                    ZStack {
                        Color.black.opacity(0.5)
                            .edgesIgnoringSafeArea(.all)
                        
                        VStack {
                            Button(action: {
                                withAnimation {
                                    isConnectingToSpeaker.toggle()
                                }
                            }) {
                                Image(systemName: "xmark")
                                    .foregroundColor(.white)
                                    .font(.headline)
                            }
                            .padding(.top, 20)
                            .padding(.trailing, 20)
                            Spacer()
                            ScrollView(.horizontal) {
                                HStack(spacing: 0) {
                                    Image("1")
                                        .resizable()
                                        .aspectRatio(contentMode: .fit)
                                        .frame(width: UIScreen.main.bounds.width)
                                    Image("2")
                                        .resizable()
                                        .aspectRatio(contentMode: .fit)
                                        .frame(width: UIScreen.main.bounds.width)
                                    Image("3")
                                        .resizable()
                                        .aspectRatio(contentMode: .fit)
                                        .frame(width: UIScreen.main.bounds.width)
                                    Image("4")
                                        .resizable()
                                        .aspectRatio(contentMode: .fit)
                                        .frame(width: UIScreen.main.bounds.width)
                                    Image("5")
                                        .resizable()
                                        .aspectRatio(contentMode: .fit)
                                        .frame(width: UIScreen.main.bounds.width)
                                }
                            }
                            Spacer()
                        }
                    }
                    .transition(.opacity)
                }
            }
            .onAppear {
                setupAudioEngine()
            }
            .navigationBarHidden(true)
            .onReceive(NotificationCenter.default.publisher(for: AVAudioSession.routeChangeNotification)) { _ in
                // Handle audio route changes if needed
            }
        }
        .navigationViewStyle(StackNavigationViewStyle())
    }

    func startAudioEngine() {
        do {
            try audioEngine.start()
            isAudioEngineRunning = true
        } catch {
            print("Error starting audio engine: \(error.localizedDescription)")
        }
    }

    func stopAudioEngine() {
        audioEngine.stop()
        isAudioEngineRunning = false
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
