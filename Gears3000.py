import adsk.core
import adsk.fusion
import traceback
import math

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        buttonDef = cmdDefs.addButtonDefinition('Gears3000', 'Gears3000', 'Create Gears based on connected sketch circles', './resources')

        # Connect to the command created event.
        commandCreatedEvent = buttonDef.commandCreated
        commandCreatedEvent.add(onCommandCreated)

        # Execute the command definition.
        buttonDef.execute()

        # Keep the script running.
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def onCommandCreated(args):
    try:
        command = args.command
        inputs = command.commandInputs

        # Create a selection input.
        circleSelection = inputs.addSelectionInput('circleSelection', 'Select Circles', 'Select the sketch circles to create gears')
        circleSelection.setSelectionLimits(1)

        # Create a checkbox input for helical gears.
        helicalCheckbox = inputs.addBoolValueInput('helicalCheckbox', 'Helical Gears', True)

        # Create a checkbox input for bevel gears.
        bevelCheckbox = inputs.addBoolValueInput('bevelCheckbox', 'Bevel Gears', False)

        # Create inputs for new options.
        thicknessInput = inputs.addValueInput('thickness', 'Thickness', 'mm', adsk.core.ValueInput.createByReal(1))
        holeDiameterInput = inputs.addValueInput('holeDiameter', 'Hole Diameter', 'mm', adsk.core.ValueInput.createByReal(1))
        backlashInput = inputs.addValueInput('backlash', 'Backlash', 'mm', adsk.core.ValueInput.createByReal(0.1))
        pressureAngleInput = inputs.addValueInput('pressureAngle', 'Pressure Angle', 'deg', adsk.core.ValueInput.createByReal(20))
        moduleInput = inputs.addValueInput('module', 'Module', 'mm', adsk.core.ValueInput.createByReal(1))

        # Connect to the execute event.
        command.execute.add(onExecute)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def onExecute(args):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Get the input values.
        circleSelection = args.command.commandInputs.itemById('circleSelection')
        selectedCircles = circleSelection.selection(0)
        helicalCheckbox = args.command.commandInputs.itemById('helicalCheckbox')
        isHelical = helicalCheckbox.value
        bevelCheckbox = args.command.commandInputs.itemById('bevelCheckbox')
        isBevel = bevelCheckbox.value

        # Get the new option values.
        thickness = args.command.commandInputs.itemById('thickness').value
        holeDiameter = args.command.commandInputs.itemById('holeDiameter').value
        backlash = args.command.commandInputs.itemById('backlash').value
        pressureAngle = args.command.commandInputs.itemById('pressureAngle').value
        module = args.command.commandInputs.itemById('module').value

        # Create gears based on the selected circles.
        createGears(selectedCircles, isHelical, isBevel, thickness, holeDiameter, backlash, pressureAngle, module)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createGears(selectedCircles, isHelical, isBevel, thickness, holeDiameter, backlash, pressureAngle, module):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Create a new component for the gears.
        rootComp = design.rootComponent
        gearComp = rootComp.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
        gearComp.name = "Gears3000"

        # Create the gears based on the selected circles.
        for circle in selectedCircles:
            # Create a new sketch on the circle's plane.
            sketch = gearComp.sketches.add(circle.geometry.plane)

            # Project the circle onto the sketch.
            sketch.project(circle)

            # Create the gear based on the projected circle.
            createGear(sketch, circle, isHelical, isBevel, thickness, holeDiameter, backlash, pressureAngle, module)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createGear(sketch, circle, isHelical, isBevel, thickness, holeDiameter, backlash, pressureAngle, module):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Calculate the number of teeth based on the module and circle diameter
        numTeeth = int(circle.geometry.radius * 2 / module)

        # Calculate the diametral pitch based on the module
        diametralPitch = numTeeth / (circle.geometry.radius * 2)

        # Create the gear using the drawGear function
        gear = drawGear(design, diametralPitch, numTeeth, thickness, 0, pressureAngle, backlash, holeDiameter)

        # Create helical gear if requested.
        if isHelical:
            createHelicalGear(gear, thickness, holeDiameter, backlash, pressureAngle, module)

        # Create bevel gear if requested.
        if isBevel:
            createBevelGear(gear, thickness, holeDiameter, backlash, pressureAngle, module)
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createHelicalGear(gear, thickness, holeDiameter, backlash, pressureAngle, module):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Create a coil feature for the helical gear.
        coils = design.rootComponent.features.coilFeatures
        coilInput = coils.createInput(gear.bodies.item(0), adsk.fusion.CoilFeatureOperations.CutFeatureOperation)

        # Set the coil parameters.
        coilInput.height = adsk.core.ValueInput.createByReal(thickness)
        coilInput.diameter = adsk.core.ValueInput.createByReal(holeDiameter)
        coilInput.pitch = adsk.core.ValueInput.createByReal(backlash)
        coilInput.isClockwise = True
        coilInput.isSolid = False

        # Create the helical gear.
        helicalGear = coils.add(coilInput)

        # Rename the helical gear body.
        helicalGear.bodies.item(0).name = "Helical Gear"
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def createBevelGear(gear, thickness, holeDiameter, backlash, pressureAngle, module):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        design = app.activeProduct

        # Create a draft feature for the bevel gear.
        drafts = design.rootComponent.features.draftFeatures
        draftInput = drafts.createInput(gear.bodies.item(0), adsk.core.ValueInput.createByReal(pressureAngle))

        # Set the draft parameters.
        draftInput.isTangentChain = True

        # Create the bevel gear.
        bevelGear = drafts.add(draftInput)

        # Rename the bevel gear body.
        bevelGear.bodies.item(0).name = "Bevel Gear"
    except:
        ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Calculate points along an involute curve.
def involutePoint(baseCircleRadius, distFromCenterToInvolutePoint):
    try:
        # Calculate the other side of the right-angle triangle defined by the base circle and the current distance radius.
        # This is also the length of the involute chord as it comes off of the base circle.
        triangleSide = math.sqrt(math.pow(distFromCenterToInvolutePoint,2) - math.pow(baseCircleRadius,2)) 
        
        # Calculate the angle of the involute.
        alpha = triangleSide / baseCircleRadius

        # Calculate the angle where the current involute point is.
        theta = alpha - math.acos(baseCircleRadius / distFromCenterToInvolutePoint)

        # Calculate the coordinates of the involute point.    
        x = distFromCenterToInvolutePoint * math.cos(theta)
        y = distFromCenterToInvolutePoint * math.sin(theta)

        # Create a point to return.        
        return adsk.core.Point3D.create(x, y, 0)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# Builds a spur gear.
def drawGear(design, diametralPitch, numTeeth, thickness, rootFilletRad, pressureAngle, backlash, holeDiam):
    try:
        # The diametral pitch is specified in inches but everthing
        # here expects all distances to be in centimeters, so convert
        # for the gear creation.
        diametralPitch = diametralPitch / 2.54
    
        # Compute the various values for a gear.
        pitchDia = numTeeth / diametralPitch
        
        if (diametralPitch < (20 *(math.pi/180))-0.000001):
            dedendum = 1.157 / diametralPitch
        else:
            circularPitch = math.pi / diametralPitch
            if circularPitch >= 20:
                dedendum = 1.25 / diametralPitch
            else:
                dedendum = (1.2 / diametralPitch) + (.002 * 2.54)                

        rootDia = pitchDia - (2 * dedendum)
        
        baseCircleDia = pitchDia * math.cos(pressureAngle)
        outsideDia = (numTeeth + 2) / diametralPitch
        
        # Create a new component by creating an occurrence.
        occs = design.rootComponent.occurrences
        mat = adsk.core.Matrix3D.create()
        newOcc = occs.addNewComponent(mat)        
        newComp = adsk.fusion.Component.cast(newOcc.component)
        
        # Create a new sketch.
        sketches = newComp.sketches
        xyPlane = newComp.xYConstructionPlane
        baseSketch = sketches.add(xyPlane)

        # Draw a circle for the base.
        baseSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), rootDia/2.0)
        
        # Draw a circle for the center hole, if the value is greater than 0.
        prof = adsk.fusion.Profile.cast(None)
        if holeDiam - (_app.pointTolerance * 2) > 0:
            baseSketch.sketchCurves.sketchCircles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), holeDiam/2.0)

            # Find the profile that uses both circles.
            for prof in baseSketch.profiles:
                if prof.profileLoops.count == 2:
                    break
        else:
            # Use the single profile.
            prof = baseSketch.profiles.item(0)
        
        #### Extrude the circle to create the base of the gear.

        # Create an extrusion input to be able to define the input needed for an extrusion
        # while specifying the profile and that a new component is to be created
        extrudes = newComp.features.extrudeFeatures
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Define that the extent is a distance extent of 5 cm.
        distance = adsk.core.ValueInput.createByReal(thickness)
        extInput.setDistanceExtent(False, distance)

        # Create the extrusion.
        baseExtrude = extrudes.add(extInput)
        
        # Create a second sketch for the tooth.
        toothSketch = sketches.add(xyPlane)

        # Calculate points along the involute curve.
        involutePointCount = 
