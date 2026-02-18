@object context // Just object (And it's just comment)
  task: "Our
  favorite
  hikes
  together" // Multiline value
  location: Boulder
  season: spring_2025

// Possible types: string, number, bool, object{type,type}, array{type}
@array friends[4]{string}
  ana,luis,sam, // Will processed any values separated by commas
  "And others: den,alex,diana" // Commas will ignored if string wrapped in quotes

// Sequence of structured data, same as CSV
@dataset hikes[3]{id string,name string,distanceKm number,elevationGain number,companion string,wasSunny bool}
  1,Blue Lake Trail,7.5,320,ana,true
  2,Ridge Overlook,9.2,540,luis,false
  3,Wildflower Loop,5.1,180,sam,true

@type Hike // Type definition named Hike
  id string
  name string
  distanceKm number
  elevationGain number
  companion string
  wasSunny bool

// Same hikes
@dataset hikesAsHikeType[3]{Hike}
  1,Blue Lake Trail,7.5,320,ana,true
  2,Ridge Overlook,9.2,540,luis,false
  3,Wildflower Loop,5.1,180,sam,true

// Hike object as field type
@dataset achievements[3]{id number, person, string, hike Hike}
  1,Me,{1,Blue Lake Trail,7.5,320,ana,true}
  2,You,{2,Ridge Overlook,9.2,540,luis,false}
  3,Us,{3,Wildflower Loop,5.1,180,sam,true}


// Feature
@graph hikesGraph[3]{id number, name string, near @relation}
  1,Blue Lake Trail,@1@2 // Indexes
  2,Ridge Overlook,@0:0.1@2:0.9 // Can be weighted
  3,Wildflower Loop,@0@1
